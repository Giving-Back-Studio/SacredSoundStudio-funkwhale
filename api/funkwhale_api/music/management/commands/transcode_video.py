import os
import tempfile
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from funkwhale_api.music.models import Upload, UploadVersion
from funkwhale_api.music import utils

class Command(BaseCommand):
    help = 'Transcode a video file and create UploadVersion records for each resolution'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str, help='Upload file name')

    def handle(self, *args, **options):
        file_name = options['file_name']
        
        # Find upload based on file path
        try:
            upload = Upload.objects.get(video_file=file_name)
        except Upload.DoesNotExist:
            self.stderr.write(f"Could not find Upload record for file {file_name}")
            return

        if not upload.video_file:
            self.stderr.write(f"Upload {upload.uuid} has no video file")
            return
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download source file
            input_file = os.path.join(temp_dir, "input.mp4")
            self.stdout.write("Downloading source video file...")
            with open(input_file, 'wb') as f:
                f.write(upload.video_file.read())

            # Transcode to each resolution
            for settings in utils.TRANSCODE_SETTINGS:
                output_file = os.path.join(temp_dir, f"output_{settings['suffix']}.mp4")
                self.stdout.write(f"Transcoding {settings['suffix']} version...")

                try:
                    utils.transcode_video(
                        input_path=input_file,
                        output_path=output_file,
                        resolution=settings['resolution'],
                        video_bitrate=settings['video_bitrate'],
                        maxrate=settings['maxrate'],
                        bufsize=settings['bufsize'],
                        audio_bitrate=settings['audio_bitrate']
                    )
                except Exception as e:
                    self.stderr.write(f"Transcoding failed for {settings['suffix']}: {str(e)}")
                    continue

                # Get video metadata
                video_data = utils.get_video_file_data(output_file)
                if not video_data:
                    self.stderr.write(f"Could not get video metadata for {settings['suffix']}")
                    continue

                # Create UploadVersion record
                version = UploadVersion(
                    upload=upload,
                    mimetype='video/mp4',
                    bitrate=int(settings['video_bitrate'].rstrip('k')),
                    size=os.path.getsize(output_file)
                )

                # Save the transcoded file to the UploadVersion
                with open(output_file, 'rb') as f:
                    version.video_file.save(
                        f"{upload.uuid}_{settings['suffix']}.mp4",
                        ContentFile(f.read()),
                        save=False
                    )
                version.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created {settings['suffix']} version (UploadVersion {version.id})"
                    )
                )

            self.stdout.write(self.style.SUCCESS("Video transcoding complete"))
