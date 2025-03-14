import mimetypes
import os
import pathlib
import logging

import ffmpeg
import magic
import mutagen
import pydub
from django.conf import settings
from django.core.cache import cache
from django.db.models import F

from funkwhale_api.common import throttling
from funkwhale_api.common.search import get_fts_query  # noqa
from funkwhale_api.common.search import get_query  # noqa
from funkwhale_api.common.search import normalize_query  # noqa

logger = logging.getLogger(__name__)

def guess_mimetype(f):
    b = min(1000000, f.size)
    t = magic.from_buffer(f.read(b), mime=True)
    if not t.startswith("audio/"):
        t = guess_mimetype_from_name(f.name)

    return t


def guess_mimetype_from_name(name):
    # failure, we try guessing by extension
    mt, _ = mimetypes.guess_type(name)
    if mt:
        t = mt
    else:
        t = EXTENSION_TO_MIMETYPE.get(name.split(".")[-1])
    return t


def compute_status(jobs):
    statuses = jobs.order_by().values_list("status", flat=True).distinct()
    errored = any([status == "errored" for status in statuses])
    if errored:
        return "errored"
    pending = any([status == "pending" for status in statuses])
    if pending:
        return "pending"
    return "finished"


AUDIO_EXTENSIONS_AND_MIMETYPE = [
    # keep the most correct mimetype for each extension at the bottom
    ("mp3", "audio/mp3"),
    ("mp3", "audio/mpeg3"),
    ("mp3", "audio/x-mp3"),
    ("mp3", "audio/mpeg"),
    ("ogg", "video/ogg"),
    ("ogg", "audio/ogg"),
    ("opus", "audio/opus"),
    ("aac", "audio/x-m4a"),
    ("m4a", "audio/x-m4a"),
    ("flac", "audio/x-flac"),
    ("flac", "audio/flac"),
    ("aif", "audio/aiff"),
    ("aif", "audio/x-aiff"),
    ("aiff", "audio/aiff"),
    ("aiff", "audio/x-aiff"),
]

EXTENSION_TO_MIMETYPE = {ext: mt for ext, mt in AUDIO_EXTENSIONS_AND_MIMETYPE}
MIMETYPE_TO_EXTENSION = {mt: ext for ext, mt in AUDIO_EXTENSIONS_AND_MIMETYPE}

SUPPORTED_EXTENSIONS = list(sorted({ext for ext, _ in AUDIO_EXTENSIONS_AND_MIMETYPE}))


def get_ext_from_type(mimetype):
    return MIMETYPE_TO_EXTENSION.get(mimetype)


def get_type_from_ext(extension):
    if extension.startswith("."):
        # we remove leading dot
        extension = extension[1:]
    return EXTENSION_TO_MIMETYPE.get(extension)


def get_audio_file_data(f):
    data = mutagen.File(f)
    if not data:
        return
    d = {}
    d["bitrate"] = getattr(data.info, "bitrate", 0)
    d["length"] = data.info.length

    return d


def get_video_file_data(file_path):
    """Extract video metadata using ffprobe"""
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next(
            (s for s in probe['streams'] if s['codec_type'] == 'video'),
            None
        )
        format_info = probe.get('format', {})

        return {
            'duration': int(float(format_info.get('duration', 0))),
            'bitrate': int(format_info.get('bit_rate', 0)) // 1000,
            'width': video_stream.get('width') if video_stream else None,
            'height': video_stream.get('height') if video_stream else None,
            'codec': video_stream.get('codec_name') if video_stream else None,
        }
    except Exception as e:
        logger.error(f"Error extracting video metadata: {str(e)}")
        return None


def get_actor_from_request(request):
    actor = None
    if hasattr(request, "actor"):
        actor = request.actor
    elif request.user.is_authenticated:
        actor = request.user.actor

    return actor


def transcode_file(input, output, input_format=None, output_format="mp3", **kwargs):
    with input.open("rb"):
        audio = pydub.AudioSegment.from_file(input, format=input_format)
    return transcode_audio(audio, output, output_format, **kwargs)


def transcode_audio(audio, output, output_format, **kwargs):
    with output.open("wb"):
        return audio.export(output, format=output_format, **kwargs)


def transcode_video(input_path, output_path, resolution, video_bitrate, maxrate, bufsize, audio_bitrate):
    """
    Transcode a video file using ffmpeg with the specified parameters.
    
    Args:
        input_path: Path to input video file
        output_path: Path where transcoded video will be saved
        resolution: Tuple of (width, height) for output resolution
        video_bitrate: Video bitrate (e.g. '5000k')
        maxrate: Maximum bitrate (e.g. '5350k')
        bufsize: Buffer size (e.g. '7000k')
        audio_bitrate: Audio bitrate (e.g. '192k')
    """
    try:
        width, height = resolution
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            vcodec='libx264',
            acodec='aac',
            preset='medium',
            **{
                'b:v': video_bitrate,
                'maxrate': maxrate,
                'bufsize': bufsize,
                'b:a': audio_bitrate,
                'vf': f'scale={width}:{height}'
            }
        )
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode()}")
        raise

TRANSCODE_SETTINGS = [
    {
        'resolution': (1920, 1080),
        'video_bitrate': '5000k',
        'maxrate': '5350k',
        'bufsize': '7000k',
        'audio_bitrate': '192k',
        'suffix': '1080p'
    },
    {
        'resolution': (1280, 720),
        'video_bitrate': '2800k',
        'maxrate': '2996k',
        'bufsize': '4200k',
        'audio_bitrate': '128k',
        'suffix': '720p'
    },
    {
        'resolution': (854, 480),
        'video_bitrate': '1400k',
        'maxrate': '1498k',
        'bufsize': '2100k',
        'audio_bitrate': '96k',
        'suffix': '480p'
    },
    {
        'resolution': (640, 360),
        'video_bitrate': '800k',
        'maxrate': '856k',
        'bufsize': '1200k',
        'audio_bitrate': '96k',
        'suffix': '360p'
    }
]


def increment_downloads_count(upload, user, wsgi_request):
    ident = throttling.get_ident(user=user, request=wsgi_request)
    cache_key = "downloads_count:upload-{}:{}-{}".format(
        upload.pk, ident["type"], ident["id"]
    )

    value = cache.get(cache_key)
    if value:
        # download already tracked
        return

    upload.downloads_count = F("downloads_count") + 1
    upload.track.downloads_count = F("downloads_count") + 1

    upload.save(update_fields=["downloads_count"])
    upload.track.save(update_fields=["downloads_count"])

    duration = max(upload.duration or 0, settings.MIN_DELAY_BETWEEN_DOWNLOADS_COUNT)

    cache.set(cache_key, 1, duration)


def browse_dir(root, path):
    if ".." in path:
        raise ValueError("Relative browsing is not allowed")

    root = pathlib.Path(root)
    real_path = root / path

    dirs = []
    files = []
    for el in sorted(os.listdir(real_path)):
        if os.path.isdir(real_path / el):
            dirs.append({"name": el, "dir": True})
        else:
            files.append({"name": el, "dir": False})

    return dirs + files
