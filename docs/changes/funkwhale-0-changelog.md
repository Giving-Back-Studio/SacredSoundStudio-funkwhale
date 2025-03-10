# Funkwhale 0.x changelog

## 0.21.2 (2020-07-27)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

Enhancements:

- Added a new ?related=obj_id filter for artists, albums and tracks, based on tags
- Can now filter subscribed content through API (#1116)
- Support ordering=random for artists, albums, tracks and channels endpoints (#1145)
- Use role=alert on forms/toast message to improve accessibility (#1134)

Bugfixes:

- Fix embedded player not working on channel series/album (#1175)
- Fixed broken mimetype detection during import (#1165)
- Fixed crash when loading recent albums via Subsonic (#1158)
- Fixed crash with null help text in admin (#1161)
- Fixed invalid metadata when importing multi-artists tracks/albums (#1104)
- Fixed player crash when using Funkwhale as a PWA (#1157)
- Fixed wrong convert art displaying in some situations (#1138)
- Make channel card updated times more humanly readable, add internationalization (#1089)

Contributors to this release (development, documentation, reviews):

- Agate
- Bheesham Persaud
- Ciarán Ainsworth

## 0.21.1 (2020-06-11)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

Features:

- Support a --watch mode with `import_files` to automatically add, update and remove files when filesystem is updated (#721)

Enhancements:

- Added new channels widget on pod landing page (#1113)
- Fix HTML <title> not including instance name in some situations (#1107)
- Make URL-building logic more resilient against reverse proxy misconfiguration (#1085)
- Removed unused masonry dependency (#1112)
- Support for specifying itunes:email and itunes:name in channels for compatibility with third-party platforms (#1154)
- Updated the /api/v1/libraries endpoint to support listing public libraries from other users/pods (#1151)

Bugfixes:

- Added safeguard to ensure local uploads are never purged from cache (#1086)
- Ensure firefox password manager dont autofill username in search bar (#1090)
- Ensure player doesn't disappear when last queue track is removed manually (#1092)
- Ensure tracks linked to skipped upload can be pruned (#1011)
- Fix playlist modal only listing 50 first playlists (#1087)
- Fixed a wording issue on artist channel page (#1117)
- Fixed crash on python 3.5 with cli importer (#1155)
- Fixed issue when displaying starred tracks on subsonic (#1082)
- Fixed mimetype detection issue that broke transcoding on some tracks (#1093). Run `python manage.py fix_uploads --mimetype` to set proper mimetypes on existing uploads.
- Fixed page not refreshing when switching between My Library and Explore sections (#1091)
- Fixed recursive CLI importing crashing under Python 3.5 (#1148, #1147)
- Fixed wrong album and track count in admin artist API (#1096)
- Include tracks by album artist when filtering by artist on /api/v1/tracks (#1078)

### Small API breaking change in `/api/v1/libraries`

To allow easier crawling of public libraries on a pod,we had to make a slight breaking change
to the behaviour of `GET /api/v1/libraries`.

Before, it returned only libraries owned by the current user.

Now, it returns all the accessible libraries (including ones from other users and pods).

If you are consuming the API via a third-party client and need to retrieve your libraries,
use the `scope` parameter, like this: `GET /api/v1/libraries?scope=me`

Contributors to this release (development, documentation, reviews, testing):

- Agate
- Ciarán Ainsworth
- Creak
- gisforgabriel
- Siren
- Tony Wasserka

## 0.21 "Agate" (2020-04-24)

This 0.21 release is dedicated to Agate, to thank her, for both having created the Funkwhale project, being the current lead developer, and for her courage of coming out. Thank you Agate from all the members of the Funkwhale community <3

We are truly grateful as well to the dozens of people who contributed to this release with translations, development, documentation, reviews, design, testing, feedback, financial support, third-party projects and integrations… You made it possible!

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html, there are also additional operations you need to execute, listed in the changelog below (search "Manual action").

### Channels and podcasts

Funkwhale 0.21 includes a brand new feature: Channels!

Channels can be used as a replacement to public libraries,
to publish audio content, both musical and non-musical. They federate with other Funkwhale pods, but also other
fediverse software, in particular Mastodon, Pleroma, Friendica and Reel2Bits, meaning people can subscribe to your channel
from any of these software. To get started with publication, simply visit your profile and create a channel from there.

Each Funkwhale channel also comes with RSS feed that is compatible with existing podcasting applications, like AntennaPod
on Android and, within Funkwhale, you can also subscribe to any podcast from its RSS feed!

Many, many thanks to the numerous people who helped with the feature design, development and testing, and in particular
to the members of the working group who met every week for months in order to get this done, and the members of other third-party
projects who took the time to work with us to ensure compatibility.

### Redesigned navigation, player and queue

This release includes a full redesign of our navigation, player and queue. Overall, it should provide
a better, less confusing experience, especially on mobile devices. This redesign was suggested
14 months ago, and took a while, but thanks to the involvement and feedback of many people, we got it done!

### Improved search bar for searching remote objects

The search bar now support fetching arbitrary objects using a URL. In particular, you can use this to quickly:

- Subscribe to a remote library via its URL
- Listen a public track from another pod
- Subscribe to a channel

### Screening for sign-ups and custom sign-up form

Instance admins can now configure their pod so that registrations required manual approval from a moderator. This
is especially useful on private or semi-private pods where you don't want to close registrations completely,
but don't want spam or unwanted users to join your pod.

When this is enabled and a new user register, their request is put in a moderation queue, and moderators
are notified by email. When the request is approved or refused, the user is also notified by email.

In addition, it's also possible to customize the sign-up form by:

- Providing a custom help text, in markdown format
- Including additional fields in the form, for instance to ask the user why they want to join. Data collected through these fields is included in the sign-up request and viewable by the mods

### Federated reports

It's now possible to send a copy of a report to the server hosting the reported object, in order to make moderation easier and more distributed.

This feature is inspired by Mastodon's current design, and should work with at least Funkwhale and Mastodon servers.

### Improved search performance

Our search engine went through a full rewrite to make it faster. This new engine is enabled
by default when using the search bar, or when searching for artists, albums and tracks. It leverages
PostgreSQL full-text search capabilities.

During our tests, we observed huge performance improvements after the switch, by an order of
magnitude. This should be especially perceptible on pods with large databases, more modest hardware
or hard drives.

We plan to remove the old engine in an upcoming release. In the meantime, if anything goes wrong,
you can switch back by setting `USE_FULL_TEXT_SEARCH=false` in your `.env` file.

### Enforced email verification

The brand new `ACCOUNT_EMAIL_VERIFICATION_ENFORCE` setting can be used to make email verification
mandatory for your users. It defaults to `false`, and doesn't apply to superuser accounts created through
the CLI.

If you enable this, ensure you have a SMTP server configured too.

### More reliable CLI importer [manual action required]

Our CLI importer is now more reliable and less prone to Out-of-Memory issues, especially when scanning large libraries. (hundreds of GB or bigger)

We've also improved the directory crawling logic, so that you don't have to use glob patterns or specify extensions when importing. As a result, the syntax for providing directories to the command as changed slightly.

If you use the `import_files` command, this means you should replace scripts that look like this:

```sh
python api/manage.py import_files $LIBRARY_ID "/srv/funkwhale/data/music/**/*.ogg" "/srv/funkwhale/data/music/**/*.mp3" --recursive --noinput
```

By this:

```sh
python api/manage.py import_files $LIBRARY_ID "/srv/funkwhale/data/music/" --recursive --noinput
```

And Funkwhale will happily import any supported audio file from the specified directory.

### User management through the server CLI

We now support user creation (incl. non-admin accounts), update and removal directly
from the server CLI. Typical use cases include:

- Changing a user password from the command line
- Creating or updating users from deployments scripts or playbooks
- Removing or granting permissions or upload quota to multiple users at once
- Marking multiple users as inactive

All user-related commands are available under the `python manage.py fw users` namespace.
Please refer to the [Admin documentation](https://docs.funkwhale.audio/admin/commands.html#user-management) for
more information and instructions.

### Progressive web app [Manual action suggested, non-docker only]

We've made Funkwhale's Web UI a Progressive Web Application (PWA), in order to improve the user experience
during offline use, and on mobile devices.

In order to fully benefit from this change, if your pod isn't deployed using Docker, ensure
the following instruction is present in your nginx configuration:

```nginx
location /front/ {
    # Add the following line in the /front/ location
    add_header Service-Worker-Allowed "/";
}
```

### Postgres docker changed environment variable [manual action required, docker multi-container only]

If you're running with docker and our multi-container setup, there was a breaking change starting in the 11.7 postgres image (https://github.com/docker-library/postgres/pull/658)

You need to add this to your .env file: `POSTGRES_HOST_AUTH_METHOD=trust`

Newer deployments aren't affected.

### Upgrade from Postgres 10 to 11 [manual action required, docker all-in-one only]

With our upgrade to Alpine 3.10, the `funkwhale/all-in-one` image now includes PostgreSQL 11.

In order to update to Funkwhale 0.21, you will first need to upgrade Funkwhale's PostgreSQL database, following the steps below:

```sh
# open a shell as the Funkwhale user
sudo -u funkwhale -H bash

# move to the funkwhale data directory
# (replace this with your own if you used a different path)
cd /srv/funkwhale/data

# stop the funkwhale container
docker stop funkwhale

# backup the database files
cp -r data/ ../postgres.bak

# Upgrade the database
docker run --rm \
    -v $(pwd)/data:/var/lib/postgresql/10/data \
    -v $(pwd)/upgraded-postgresql:/var/lib/postgresql/11/data \
    -e PGUSER=funkwhale \
    -e POSTGRES_INITDB_ARGS="-U funkwhale --locale C --encoding UTF8" \
    tianon/postgres-upgrade:10-to-11

# replace the Postgres 10 files with Postgres 11 files
mv data/ postgres-10
mv upgraded-postgresql/ data
```

Once you have completed the Funkwhale upgrade with our regular instructions and everything works properly,
you can remove the backups/old files:

```sh
sudo -u funkwhale -H bash
cd /srv/funkwhale/data
rm -rf ../postgres.bak
rm -rf postgres-10
```

### Full list of changes

Features:

- Support for publishing and subscribing to podcasts (#170)
- Brand new navigation, queue and player redesign (#594)
- Can now browse a library content through the UI (#926)
- Federated reports (#1038)
- Screening for sign-ups (#1040)
- Make it possible to enforce email verification (#1039)
- Added a new radio based on another user listenings (#1060)
- User management through the server CLI

Enhancements:

- Added ability to reject library follows from notifications screen (#859)
- Added periodic background task and CLI command to associate genre tags to artists and albums based on identical tags found on corresponding tracks (#988)
- Added support for CELERYD_CONCURRENCY env var to control the number of worker processes (#997)
- Added the ability to sort albums by release date (#1013)
- Added two new radios to play your own content or a given library tracks
- Advertise list of known nodes on /api/v1/federation/domains and in nodeinfo if stats sharing is enabled
- Changed footer to use instance name if available, and append ellipses if instance URL/Name is too long (#1012)
- Favor local uploads when playing a track with multiple uploads (#1036)
- Include only local content in nodeinfo stats, added downloads count
- Make media and static files serving more reliable when reverse proxy `X_FORWARDED_*` headers are incorrect (#947)
- Order the playlist columns by modification date in the Browse tab (#775)
- Reduced size of funkwhale/funkwhale docker images thanks to multi-stage builds (!1042)
- Remember display settings in Album, Artist, Radio and Playlist views (#391)
- Removed unnecessary "Federation music needs approval" setting (#959)
- Replaced our slow research logic by PostgreSQL full-text search (#994)
- Support autoplay when loading embed frame from Mastodon and third-party websites (#1041)
- Support filtering playlist by name and several additional UX improvements in playlists modal (#974)
- Support modifying album cover art through the web UI (#588)
- Use a dedicated scope for throttling subsonic to avoid intrusive rate-limiting
- Use same markdown widget for all content fields (rules, description, reports, notes, etc.)
- CLI Importer is now more reliable and less resource-hungry on large libraries
- Add support custom domain for S3 storage
- Better placeholders for channels when there are no episodes or series
- Updated documentation for 0.21 release
- Improved performance and error handling when fetching remote attachments

Bugfixes:

- Added missing manuallyApprovesFollowers entry in JSON-LD contexts (#961)
- Fix issue with browser shortcuts such as search and focus URL not being recognised (#340, #985)
- Fixed admin dropdown not showing after login (#1042)
- Fixed an issue with celerybeat container failing to restart (#1004)
- Fixed invalid displayed number of tracks in playlist (#986)
- Fixed issue with recent results not being loaded from the API (#948)
- Fixed issue with sorting by album name not working (#960)
- Fixed short audio glitch when switching switching to another track with player paused (#970)
- Improved deduplication logic to prevent skipped files during import (#348, #474, #557, #740, #928)
- More resilient tag parsing with empty release date or album artist (#1037)
- More robust importer against malformed dates (#966)
- Removed "nodeinfo disabled" setting, as nodeinfo is required for the UI to work (#982)
- Replaced PDF icon by List icon in playlist placeholder (#943)
- Resolve an issue where disc numbers were not taken into consideration when playing an album from the album card (#1006)
- Set correct size for album covers in playlist cards (#680)
- Remove double spaces in ChannelForm
- Deduplicate tags in Audio ActivityPub representation
- Add support custom domain for S3 storage
- Fix #1079: fixed z-index issues with dropdowns (#1079 and #1075)
- Exclude external podcasts from library home
- Fixed broken channel save when description is too long
- Fixed 500 error when federation is disabled and application+json is requested
- Fixed minor subsonic API crash
- Fixed broken local profile page when allow-list is enabled
- Fixed issue with confirmation email not sending when signup-approval was enabled
- Ensure 0 quota on user is honored
- Fixed attachments URL not honoring media URL
- Fix grammar in msg string in TrackBase.vue
- Fix typo in SubscribeButton.vue

Translations:

- Arabic
- Catalan
- English (United Kingdom)
- German
- Hungarian
- Japanese
- Occitan
- Portuguese (Brazil)
- Russian

Contributors to this release (translation, development, documentation, reviews, design, testing, third-party projects):

- Agate
- annando
- Anton Strömkvist
- Audrey
- ButterflyOfFire
- Ciarán Ainsworth
- Creak
- Daniele Lira Mereb
- dashie
- Eloisa
- eorn
- Francesc Galí
- gerhardbeck
- GinnyMcQueen
- guillermau
- Haelwenn
- jinxx
- Jonathan Aylard
- Keunes
- M.G
- marzzzello
- Mathé Grievink
- Mélanie Chauvel
- Mjourdan
- Morgan Kesler
- Noe Gaumont
- Noureddine HADDAG
- Ollie
- Peter Wickenberg
- Quentin PAGÈS
- Renon
- Satsuki Yanagi
- Shlee
- SpcCw
- techknowlogick
- ThibG
- Tony Wasserka
- unklebonehead
- wakest
- wxcafé
- Xaloc
- Xosé M

## 0.20.1 (2019-10-28)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

### Denormalized audio permission logic in a separate table to enhance performance

With this release, we're introducing a performance enhancement that should reduce the load on the database and API
servers (cf https://dev.funkwhale.audio/funkwhale/funkwhale/merge_requests/939).

Under the hood, we now maintain a separate table to link users to the tracks they are allowed to see. This change is **disabled**
by default, but should be enabled by default starting in Funkwhale 0.21.

If you want to try it now, add
`MUSIC_USE_DENORMALIZATION=True` to your `.env` file, restart Funkwhale, and run the following command:

```sh
python manage.py rebuild_music_permissions
```

This shouldn't cause any regression, but we'd appreciate if you could test this before the 0.21 release and report any unusual
behaviour regarding tracks, albums and artists visibility.

Enhancements:

- Added a retry option for failed uploads (#942)
- Added feedback via loading spinner when searching a remote library
- Denormalized audio permission logic in a separate table to enhance performance
- Placeholders will now be shown if no content is available across the application (#750)
- Reduce the number of simultaneous DB connections under some deployment scenario
- Support byYear filtering in Subsonic API (#936)

Bugfixes:

- Ensure password input doesn't overflow outside of container (#933)
- Fix audio serving issues under S3/nginx when signatures are enabled
- Fix import crash when importing M4A file with no embedded cover (#946)
- Fix tag exclusion in custom radios (#950)
- Fixed an issue with embed player CSS being purged during build (#935)
- Fixed escaped pod name displayed on home/about page (#945)
- Fixed pagination in subsonic getSongsByGenre endpoint (#954)
- Fixed style glitches in dropdowns

Documentation:

- Documented how to create DB extension by hand in case of permission error during migrations (#934)

Contributors to this release (translation, development, documentation, reviews, design):

- Ciarán Ainsworth
- Dag Stenstad
- Daniele Lira Mereb
- Agate
- Esteban
- Johannes H.
- knuxify
- Mateus Mattei Garcia
- Quentin PAGÈS

## 0.20 (2019-10-04)

Upgrade instructions are available at https://docs.funkwhale.audio/admin/upgrading.html

### Support for genres via tags

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

One of our most requested missing features is now available!

Starting with Funkwhale 0.20,
Funkwhale will automatically extract genre information from uploaded files and associate it
with the corresponding tracks in the form of tags (similar to Mastodon or Twitter hashtags).
Please refer to [our tagging documentation](https://docs.funkwhale.audio/users/upload.html#tagging-files)
for more information regarding the tagging process.

Tags can also be associated with artists and albums, and updated after upload through the UI using
the edit system released in Funkwhale 0.19. Tags are also fetched when retrieving content
via federation.

Tags are used in various places to enhance user experience:

- Tags are listed on tracks, albums and artist profiles
- Each tag has a dedicated page were you can browse corresponding content and quickly start a radio
- The custom radio builder now supports using tags
- Subsonic apps that support genres - such as DSub or Ultrasonic - should display this information as well

If you are a pod admin and want to extract tags from already uploaded content, you run [this snippet](https://dev.funkwhale.audio/funkwhale/funkwhale/snippets/43)
and [this snippet](https://dev.funkwhale.audio/funkwhale/funkwhale/snippets/44) in a `python manage.py shell`.

### Content and account reports

It is now possible to report content, such as artists, tracks or libraries, as well as user accounts. Such reports are forwarded to the pod moderators,
who can review it and delete reported content, block accounts or take any other action they deem necessary.

By default, both anonymous and authenticated users can submit these reports. This makes sure moderators can receive and handle
takedown requests and other reports for illegal content that may be sent by third-parties without an account on the pod. However,
you can disable anonymous reports completely via your pod settings.

Federation of the reports will be supported in a future release.

For more information about this feature, please check out our documentation:

- [User documentation](https://docs.funkwhale.audio/moderator/reports.html)
- [Moderator documentation](https://docs.funkwhale.audio/users/reports.html)

### Account deletion

Users can now delete their account themselves, without involving an administrator.

The deletion process will remove any local data and objects associated with the account,
but the username won't be able to new users to avoid impersonation. Deletion is also broadcasted
to other known servers on the federation.

For more information about this feature, please check out our documentation:

- [User documentation](https://docs.funkwhale.audio/users/account.html)

### Landing and about page redesign [Manual action suggested]

In this release, we've completely redesigned the landing and about page, by making it more useful and adapted to your pod
configuration. Among other things, the landing page will now include:

- your pod and an excerpt from your pod's description
- your pod banner image, if any
- your contact email, if any
- the login form
- the signup form (if registrations are open on your pod)
- some basic statistics about your pod
- a widget including recently uploaded albums, if anonymous access is enabled

The landing page will still include some information about Funkwhale, but in a less intrusive and proeminent way than before.

Additionally, the about page now includes:

- your pod name, description, rules and terms
- your pod banner image, if any
- your contact email, if any
- comprehensive statistics about your pod
- some info about your pod configuration, such as registration and federation status or the default upload quota for new users

With this redesign, we've added a handful of additional pod settings:

- Pod banner image
- Contact email
- Rules
- Terms of service

We recommend taking a few moments to fill these accordingly to your needs, by visiting `/manage/settings`.

### Allow-list to restrict federation to trusted domains

The Allow-Listing feature grants pod moderators
and administrators greater control over federation
by allowing you to create a pod-wide allow-list.

When allow-listing is enabled, your pod's users will only
be able to interact with pods included in the allow-list.
Any messages, activity, uploads, or modifications to
libraries and playlists will only be shared with pods
on the allow-list. Pods which are not included in the
allow-list will not have access to your pod's content
or messages and will not be able to send anything to
your pod.

If you want to enable this feature on your pod, or learn more, please refer to [our documentation](https://docs.funkwhale.audio/moderator/listing.html)!

### Periodic message to incite people to support their pod and Funkwhale

Users will now be reminded on a regular basis that they can help Funkwhale by donating or contributing.

If specified by the pod admin, a separate and custom message will also be displayed in a similar way to provide instructions and links to support the pod.

Both messages will appear for the first time 15 days after signup, in the notifications tab. For each message, users can schedule a reminder for a later time, or disable the messages entirely.

### Replaced Daphne by Gunicorn/Uvicorn [manual action required, non-docker only]

To improve the performance, stability and reliability of Funkwhale's web processes,
we now recommend using Gunicorn and Uvicorn instead of Daphne. This combination unlock new use cases such as:

- zero-downtime upgrades
- configurable number of web worker processes

Based on our benchmarks, Gunicorn/Unicorn is also faster and more stable under higher workloads compared to Daphne.

To benefit from this enhancement on existing instances, you need to add `FUNKWHALE_WEB_WORKERS=1` in your `.env` file
(use a higher number if you want to have more web worker processes).

Then, edit your `/etc/systemd/system/funkwhale-server.service` and replace the `ExecStart=` line with
`ExecStart=/srv/funkwhale/virtualenv/bin/gunicorn config.asgi:application -w ${FUNKWHALE_WEB_WORKERS} -k uvicorn.workers.UvicornWorker -b ${FUNKWHALE_API_IP}:${FUNKWHALE_API_PORT}`

Then reload the configuration change with `sudo systemctl daemon-reload` and `sudo systemctl restart funkwhale-server`.

### Content-Security-Policy and additional security headers [manual action suggested]

To improve the security and reduce the attack surface in case of a successful exploit, we suggest
you add the following Content-Security-Policy to your nginx configuration.

````{note}
If you are using an S3-compatible store to serve music, you will need to specify the URL of your S3 store in the ``media-src`` and ``img-src`` headers

```nginx
add_header Content-Security-Policy "...img-src 'self' https://<your-s3-URL> data:;...media-src https://<your-s3-URL> 'self' data:";
```
````

**On non-docker setups**, in `/etc/nginx/sites-available/funkwhale.conf`:

```nginx
server {

    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    location /front/ {
        add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
        add_header Referrer-Policy "strict-origin-when-cross-origin";
        add_header X-Frame-Options "SAMEORIGIN";
        # … existing content here
    }

    # Also create a new location for the embeds to ensure external iframes work
    # Simply copy-paste the /front/ location, but replace the following lines:
    location /front/embed.html {
        add_header X-Frame-Options "ALLOW";
        alias ${FUNKWHALE_FRONTEND_PATH}/embed.html;
    }
}
```

Then reload nginx with `systemctl reload nginx`.

**On docker setups**, in `/srv/funkwhalenginx/funkwhale.template`:

```nginx
server {

    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    location /front/ {
        add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
        add_header Referrer-Policy "strict-origin-when-cross-origin";
        add_header X-Frame-Options "SAMEORIGIN";
        # … existing content here
    }

    # Also create a new location for the embeds to ensure external iframes work
    # Simply copy-paste the /front/ location, but replace the following lines:
    location /front/embed.html {
        add_header X-Frame-Options "ALLOW";
        alias /frontend/embed.html;
    }
}

```

Then reload nginx with `docker-compose restart nginx`.

### Rate limiting

With this release, rate-limiting on the API is enabled by default, with high enough limits to ensure
regular users of the app aren't affected. Requests beyond allowed limits are answered with a 429 HTTP error.

For anonymous requests, the limit is applied to the IP address of the client, and for authenticated requests, the limit
is applied to the corresponding user account. By default, anonymous requests get a lower limit than authenticated requests.

You can disable the rate-limiting feature by adding `THROTTLING_ENABLED=false` to your `.env` file and restarting the
services. If you are using the Funkwhale API in your project or app and want to know more about the limits, please consult https://docs.funkwhale.audio/swagger/.

### Broken audio streaming when using S3/Minio and DSub [manual action required]

Some Subsonic clients, such as DSub, are sending an Authorization headers which was forwarded
to the S3 storage when streaming, causing some issues. If you are using S3 or a compatible storage
such as Minio, please add the following in your nginx `~ /_protected/media/(.+)` location:

```nginx
# Needed to ensure DSub auth isn't forwarded to S3/Minio, see #932
proxy_set_header Authorization "";
```

And reload your nginx process.

### Detail

Features:

- Added periodical message to incite people to support their pod and Funkwhale (#839)
- Admins can now add custom CSS from their pod settings (#879)
- Allow-list to restrict federation to trusted domains (#853)
- Content and account reports (#890)
- Dark theme (#756)
- Enforce a configurable rate limit on the API to mitigate abuse (#261)
- Redesign of the landing and about pages (#872)
- Support for genres, via tags (#432)
- Users can now delete their account without admin intervention (#852)

Enhancements:

- Added a info message on embed wizard when anonymous access to content is disabled (#878)
- Added Catalan translation files
- Added Czech translation (#844)
- Added field to manage user upload quota in Django backend (#903)
- Added the option to replace the queue's current contents with a selected album or track (#761)
- Artists with no albums will now show track count on artist card (#895)
- Ensure API urls answer with and without a trailing slash (#877)
- Hardcoded list of supported browsers to avoid unexpected regressions (#854)
- Hardened security thanks to CSP and additional HTTP headers (#880)
- Improve display of search results by including artist and album data
- Increase the security of JWT token generation by using DJANGO_SECRET_KEY as well as user-specific salt for the signature
- Mods can now change a library visibility through the admin UI (#548)
- New keyboard shortcuts added for enhanced control over audio player (#866)
- Now refetch remote ActivityPub artists, albums and tracks to avoid local stale data
- Numbers on the stats page will now be formatted in a human readable way and will update with the locale (#873)
- Pickup folder.png and folder.jpg files for cover art when importing from CLI (#898)
- Prevent usage of too weak passwords (#883)
- Reduced CSS size by 30% using purgecss
- Replaced Daphne by Gunicorn/Uvicorn to improve stability, flexibility and performance (#862)
- Simplified embedded docker reverse proxy IP configuration (#834)
- Support embeds on public playlists
- Support for M4A/AAC files (#661)
- Switched from Semantic-UI to Fomentic-UI
- Add dropdown menu to track table (#531)
- Display placeholder on homepage when there are no playlists (#892)
- Make album cards height independent (#710)

Bugfixes:

- Added context strings to en_GB translations so that picking the language changes the interface as expected
- Ensure selected locale is not reset to browser default when refreshing app
- Fix missing license information on track details page (#913)
- Fix regression to quota bar color (#897)
- Fixed a responsive display issues on 1024px wide screens (#904)
- Fixed album art not being retrieved from Ogg/Opus files
- Fixed broken embedded player layout after dependency update (#875)
- Fixed broken external HTTPS request under some scenarios, because of missing PyOpenSSL
- Fixed broken less listened radio (#912)
- Fixed broken URL to artist and album on album and track pages (#871)
- Fixed empty contentType causing client crash in some Subsonic payloads (#893)
- Fixed import crashing with empty cover file or too long values on some fields
- Fixed in-place imported files not playing under nginx when filename contains ? or % (#924)
- Fixed remaining transcoding issue with Subsonic API (#867)
- Fixed search usability issue when browsing artists, albums, radios and playlists (#902)
- Improved performance of /artists, /albums and /tracks API endpoints by a factor 2 (#865)
- Updated docs to ensure streaming works when using Minio/S3 and DSub (#932)

Contributors to this release (translation, development, documentation, reviews, design):

- Amaranthe
- ButterflyOfFire
- Ciarán Ainsworth
- Agate
- Esteban
- Francesc Galí
- Freyja Wildes
- hellekin
- IISergII
- jiri-novacek
- Johannes H.
- Keunes
- Koen
- Manuel Cortez
- Mehdi
- Mélanie Chauvel
- nouts
- Quentí
- Reg
- Rodrigo Leite
- Romain Failliot
- SpcCw
- Sylke Vicious
- Tobias Reisinger
- Xaloc
- Xosé M

## 0.19.1 (2019-06-28)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

Enhancements:

- The currently playing track is now highlighted with an orange play icon (#832)
- Support for importing files with no album tag (#122)
- Redirect from / to /library when user is logged in (#864)
- Added a SUBSONIC_DEFAULT_TRANSCODING_FORMAT env var to support clients that don't provide the format parameter (#867)
- Added button to search for objects on Discogs (#368)
- Added copy-to-clipboard button with Subsonic password input (#814)
- Added opus to the list of supported mimetypes and extensions (#868)
- Aligned search headers with search results in the sidebar (#708)
- Clicking on the currently selected playlist in the Playlist popup will now close the popup (#807)
- Favorites radio will not be visible if the user does not have any favorites (#419)

Bugfixes:

- Ensure empty but optional fields in file metadata don't error during import (#850)
- Fix broken upload for specific files when using S3 storage (#857)
- Fixed broken translation on home and track detail page (#833)
- Fixed broken user admin for users with non-digit or letters in their username (#869)
- Fixed invalid file extension for transcoded tracks (#848)
- Fixed issue with French translation for "Start radio" (#849)
- Fixed issue with player changing height when hovering over the volume slider (#838)
- Fixed secondary menus truncated on narrow screens (#855)
- Fixed wrong og:image url when using S3 storage (#851)
- Hide pod statistics on about page if those are disabled (#835)
- Use ASCII filename before upload to S3 to avoid playback issues (#847)

Contributors to this release (committers and reviewers):

- Ciarán Ainsworth
- Creak
- ealgase
- Agate
- Esteban
- Freyja Wildes
- hellekin
- Johannes H.
- Mehdi
- Reg

## 0.19.0 (2019-05-16)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

### Edits on tracks, albums and artists

Funkwhale was a bit annoying when it camed to metadata. Tracks, albums and artists profiles
were created from audio file tags, but basically immutable after that (unless you had
admin access to Django's UI, which wasn't ideal to do this kind of changes).

With this release, everyone can suggest changes on track, album and artist pages. Users
with the "library" permission can review suggested edits in a dedicated interface
and apply/reject them.

Approved edits are broadcasted via federation, to ensure other instances get the information
too.

Not all fields are currently modifiable using this feature. Especially, it's not possible
to suggest a new album cover, or reassign a track to a different album or artist. Those will
be implemented in a future release.

### Admin UI for tracks, albums, artists, libraries and uploads

As part of our ongoing effort to make Funkwhale easier to manage for instance owners,
this release includes a brand new administration interface to deal with:

- tracks
- albums
- artists
- libraries
- uploads

You can use this UI to quickly search for any object, delete objects in batch, understand
where they are coming from etc. This new UI should remove the need to go through Django's
admin in the vast majority of cases (but also includes a link to Django's admin when needed).

### Artist hiding in the interface

It's now possible for users to hide artists they don't want to see.

Content linked to hidden artists will not show up in the interface anymore. Especially:

- Hidden artists tracks are removed from the current queue
- Starting a playlist will skip tracks from hidden artists
- Recently favorited, recently listened and recently added widgets on the homepage won't include content from hidden artists
- Radio suggestions will exclude tracks from hidden artists
- Hidden artists won't appear in Subsonic apps

Results linked to hidden artists will continue to show up in search results and their profile page remains accessible.

### OAuth2 authorization for better integration with third-party apps

Funkwhale now support the OAuth2 authorization and authentication protocol which will allow
third-party apps to interact with Funkwhale on behalf of users.

This feature makes it possible to build third-party apps that have the same capabilities
as Funkwhale's Web UI. The only exception at the moment is for actions that requires
special permissions, such as modifying instance settings or moderation (but this will be
enabled in a future release).

If you want to start building an app on top of Funkwhale's API, please check-out
https://docs.funkwhale.audio/api.html and https://docs.funkwhale.audio/developers/authentication.html.

### Better error handling and display during import

Funkwhale should now be more resilient to missing tags in imported files, and give
you more insights when something goes wrong, including the specific tags that were missing
or invalid, and additional debug information to share in your support requests.

This information is available in all pages that list uploads, when clicking on the button next to the upload status.

### Support for S3-compatible storages to store media files

Storing all media files on the Funkwhale server itself may not be possible or desirable
in all scenarios. You can now configure Funkwhale to store those files in a S3
bucket instead.

Check-out https://docs.funkwhale.audio/admin/external-storages.html if you want to use
this feature.

### Prune library command

Users are often surprised by Funkwhale's tendency to keep track, album and artist
metadata even if no associated files exist.

To help with that, we now offer a `prune_library` management command you can run
to purge your database from obsolete entries. [Please refer to our documentation for usage instructions](https://docs.funkwhale.audio/admin/commands.html#pruning-library).

### Check in-place files command

When using in-place import with a living audio library, you'll quite often rename or
remove files from the file system. Unfortunately, Funkwhale keeps a reference to those
files in the database, which results in unplayable tracks.

To help with that, we now offer a `check_inplace_files` management command you can run
to purge your database from obsolete files. [Please refer to our documentation for usage instructions](https://docs.funkwhale.audio/admin/commands.html#remove-obsolete-files-from-database).

Features:

- Added albums view. Similar to artists view, it's viewable by clicking on the "Albums" link on the top bar. (#356)
- Allow artists hiding (#701)
- Change the document title to display current track information. (#359)
- Display a confirmation dialog when adding duplicate songs to a playlist (#784)
- Improved error handling and display during import (#252, #718, #583, #501, #544)
- Support embedding full artist discographies (#747)
- Support metadata update on tracks, albums and artists and broadcast those on the federation (#689)
- Support OAuth2 authorization for better integration with third-party apps (#752)
- Support S3-compatible storages for media files (#565)

Enhancements:

- [Experimental] Added a new "Similar" radio based on users history (suggested by @gordon)
- Added a "load more" button on artist pages to load more tracks/albums (#719)
- Added a `check_inplace_files` management command to remove purge the database from references to in-place imported files that don't exist on disk anymore (#781)
- Added a prune_library management command to remove obsolete metadata from the database (#777)
- Added admin options to disable login for users, ensure related content is deleted when deleting a user account (#809)
- Added standardized translation context for all strings in the frontend to give accurate hints to translators.
- Added twitter:\* meta tags to detect tracks and albums players automatically on more sites (#578)
  Improved responsiveness of embedded player
- Advertise the list of supported upload extensions in the Nodeinfo endpoint (#808)
- Better handling of follow/accept messages to avoid and recover from desync between instances (#830)
- Better workflow for connecting to another instance (#715)

  Changing the instance used is now better integrated in the App, and it is checked that the chosen instance and the suggested instances are valid and running Funkwhale servers.

- Bumped dependencies to latest versions (#815)
- Descriptions will now be shown underneath user libraries (#768)
- Don't store unhandled ActivityPub messages in database (#776)
- Enhanced the design of the embed wizard. (!619)
- Ensure the footer always stays at the bottom of the page
- Expose an instance-level actor (service@domain) in nodeinfo endpoint (#689)
- Improved readability of logo (#385)
- Keep persistent connections to the database instead of recreating a new one for each request
- Labels for privacy levels are now consistently grabbed from a common source instead of being hardcoded every time they are needed.
- Merged artist/album buttons with title text on artist and album pages (#725)
- Now honor maxBitrate parameter in Subsonic API (#802)
- Preload next track in queue (#572)
- Reduced app size for regular users by moving admin-related code in a dedicated chunk (#805)
- Removed broken/instable lyrics feature (#799)
- Show remaining storage space during import and prevent file upload if not enough space is remaining (#550)
- The buttons displaying an icon now always show a little divider between the icon and the text. (!620)
- Use attributedTo instead of actor in library ActivityPub payload (#619)
- Use network/depends_on instead of links in docker-compose.yml (!716)

Bugfixes:

- Add missing command from contributing file (#754)
- Add required envvar for dev environment (!668)
- Added env variable to set AWS region and signature version to serve media without proxy (#826)
- Allow users with dots in their usernames to request a subsonic password (#798)
- Better handling of featuring/multi-artist tracks tagged with MusicBrainz (#782)
- Do not consider tracks as duplicates during import if they have different positions (#740)
- Ensure all our ActivityPub fetches are authenticated (#758)
- Ensure correct track duration and playable status when browsing radios (#812)
- Fixed alignment/size issue with some buttons (#702)
- Fixed an encoding issue with instance name on about page (#828)
- Fixed cover not showing in queue/player when playing tracks from "albums" tab (#795)
- Fixed crashing upload processing on invalid date format (#718)
- Fixed dev command for fake data creation (!664)
- Fixed invalid OEmbed URL when using a local FUNKWHALE_SPA_HTML_ROOT (#824)
- Fixed invalid required fields in Upload django's admin (#819)
- Fixed issue with querying the albums api endpoint (#356)
- Fixed non-transparent background for volume range on Firefox (#722)
- Fixed overflowing input on account detail page (#791)
- Fixed unplayable radios for anonymous users (#563)
- Prevent skipping on file import if album_mbid is different (#772)
- Use proper site name/domain in emails (#806)
- Width of filter menus for radios has been set to stop text from overlapping the borders

Documentation:

- Document how to use Redis over unix sockets (#770)

Contributors to this release (committers and translators):

- Ale London
- Alexander
- Ben Finney
- ButterflyOfFire
- Ciarán Ainsworth
- Damien Nicolas
- Daniele Lira Mereb
- Agate
- Elza Gelez
- gerry_the_hat
- gordon
- interfect
- jake
- Jee
- jovuit
- Mélanie Chauvel
- nouts
- Pierrick
- Qasim Ali
- Quentí
- Renon
- Rodrigo Leite
- Sylke Vicious
- Thomas Brockmöller
- Tixie
- Vierkantor
- Von
- Zach Halasz

## 0.18.3 (2019-03-21)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

### Avoid mixed content when deploying mono-container behind proxy [Manual action required]

_You are only concerned if you use the mono-container docker deployment behind a reverse proxy_

Because of [an issue in our mono-container configuration](https://github.com/thetarkus/docker-funkwhale/issues/19), users deploying Funkwhale via docker
using our `funkwhale/all-in-one` image could face some mixed content warnings (and possibly other troubles)
when browsing the Web UI.

This is fixed in this release, but on existing deployments, you'll need to add `NESTED_PROXY=1` in your container
environment (either in your `.env` file, or via your container management tool), then recreate your funkwhale container.

Enhancements:

- Added title on hover for truncated content (#766)
- Ask for confirmation before leaving upload page if there is a an upload in process (#630)
- Exclude in-place imported files from quota computation (#570)
- Truncate filename in library file table to ensure correct display of the table. (#735)

Bugfixes:

- Avoid mixed content when deploying mono-container behind HTTPS proxy (thetarkus/docker-funkwhale#19)
- Display new notifications immediately on notifications page (#729)
- Ensure cover art from uploaded files is picked up properly on existing albums (#757)
- Fixed a crash when federating a track with unspecified position
- Fixed broken Activity and Actor modules in django admin (#767)
- Fixed broken sample apache configuration (#764)
- Fixed constant and unpredictable reordering during file upload (#716)
- Fixed delivering of local activities causing unintended side effects, such as rollbacking changes (#737)
- Fixed escaping issues in translated strings (#652)
- Fixed saving moderation policy when clicking on "Cancel" (#751)
- i18n: Update page title when changing the App's language. (#511)
- Include disc number in Subsonic responses (#765)
- Do not send notification when rejecting a follow on a local library (#743)

Documentation:

- Added documentation on mono-container docker upgrade (#713)
- Added documentation to set up let's encrypt certificate (#745)

## 0.18.2 (2019-02-13)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

Enhancements:

- Added a 'fix_federation_ids' management command to deal with protocol/domain issues in federation
  IDs after deployments (#706)
- Can now use a local file with FUNKWHALE_SPA_HTML_ROOT to avoid sending an HTTP request (#705)

Bugfixes:

- Downgraded channels dependency to 2.1.6 to fix denied uploads (#697)
- Fixed cards display issues on medium/small screens (#707)
- Fixed Embed component name that could lead to issue when developing on OSX (#696)
- Fixed resizing issues for album cards on artist pages (#694)

## 0.18.1 (2019-01-29)

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html

### Fix Gzip compression to avoid BREACH exploit [security] [manual action required]

In the 0.18 release, we've enabled Gzip compression by default for various
content types, including HTML and JSON. Unfortunately, enabling Gzip compression
on such content types could make BREACH-type exploits possible.

We've removed the risky content-types from our nginx template files, to ensure new
instances are safe, however, if you already have an instance, you need
to double check that your host nginx virtualhost do not include the following
values for the `gzip_types` settings:

```
application/atom+xml
application/json
application/ld+json
application/activity+json
application/manifest+json
application/rss+xml
application/xhtml+xml
application/xml
```

For convenience, you can also replace the whole setting with the following snippet:

```
gzip_types
application/javascript
application/vnd.geo+json
application/vnd.ms-fontobject
application/x-font-ttf
application/x-web-app-manifest+json
font/opentype
image/bmp
image/svg+xml
image/x-icon
text/cache-manifest
text/css
text/plain
text/vcard
text/vnd.rim.location.xloc
text/vtt
text/x-component
text/x-cross-domain-policy;
```

Many thanks to @jibec for the report!

### Fix Apache configuration file for 0.18 [manual action required]

The way front is served has changed since 0.18. The Apache configuration can't serve 0.18 properly, leading to blank screens.

If you are on an Apache setup, you will have to replace the `<Location "/api">` block with the following:

```apache
<Location "/">
  # similar to nginx 'client_max_body_size 100M;'
  LimitRequestBody 104857600

  ProxyPass ${funkwhale-api}/
  ProxyPassReverse ${funkwhale-api}/
</Location>
```

And add some more `ProxyPass` directives so that the `Alias` part of your configuration file looks this way:

```apache
  ProxyPass "/front" "!"
  Alias /front /srv/funkwhale/front/dist

  ProxyPass "/media" "!"
  Alias /media /srv/funkwhale/data/media

  ProxyPass "/staticfiles" "!"
  Alias /staticfiles /srv/funkwhale/data/static
```

In case you are using custom css and theming, you also need to match this block:

```apache2
  ProxyPass "/settings.json" "!"
  Alias /settings.json /srv/funkwhale/custom/settings.json

  ProxyPass "/custom" "!"
  Alias /custom /srv/funkwhale/custom
```

Enhancements:

- Added name attributes on all inputs to improve UX, especially with password managers (#686)
- Disable makemigrations in production and misleading message when running migrate (#685)
- Display progress during file upload
- Hide pagination when there is only one page of results (#681)
- Include shared/public playlists in Subsonic API responses (#684)
- Use proper locale for date-related/duration strings (#670)

Bugfixes:

- Fix transcoding of in-place imported tracks (#688)
- Fixed celery worker defaulting to development settings instead of production
- Fixed crashing Django admin when loading track detail page (#666)
- Fixed list icon alignment on landing page (#668)
- Fixed overescaping issue in notifications and album page (#676)
- Fixed wrong number of affected elements in bulk action modal (#683)
- Fixed wrong URL in documentation for funkwhale_proxy.conf file when deploying using Docker
- Make Apache configuration file work with 0.18 changes (#667)
- Removed potential BREACH exploit because of Gzip compression (#678)
- Upgraded kombu to fix an incompatibility with redis>=3

Documentation:

- Added user upload documentation at https://docs.funkwhale.audio/users/upload.html

## 0.18 "Naomi" (2019-01-22)

This release is dedicated to Naomi, an early contributor and beta tester of Funkwhale.
Her positivity, love and support have been incredibly helpful and helped shape the project
as you can enjoy it today. Thank you so much Naomi <3

Many thanks to the dozens of people that contributed to this release: translators, developers,
bug hunters, admins and backers. You made it possible!

Upgrade instructions are available at
https://docs.funkwhale.audio/administrator/upgrade/index.html, ensure you also execute the instructions
marked with `[manual action required]` and `[manual action suggested]`.

See `Full changelog` below for an exhaustive list of changes!

### Audio transcoding is back!

After removal of our first, buggy transcoding implementation, we're proud to announce
that this feature is back. It is enabled by default, and can be configured/disabled
in your instance settings!

This feature works in the browser, with federated/non-federated tracks and using Subsonic clients.
Transcoded tracks are generated on the fly, and cached for a configurable amount of time,
to reduce the load on the server.

### Licensing and copyright information

Funkwhale is now able to parse copyright and license data from file and store
this information. Apart from displaying it on each track detail page,
no additional behaviour is currently implemented to use this new data, but this
will change in future releases.

License and copyright data is also broadcasted over federation.

License matching is done on the content of the `License` tag in the files,
with a fallback on the `Copyright` tag.

Funkwhale will successfully extract licensing data for the following licenses:

- Creative Commons 0 (Public Domain)
- Creative Commons 1.0 (All declinations)
- Creative Commons 2.0 (All declinations)
- Creative Commons 2.5 (All declinations and countries)
- Creative Commons 3.0 (All declinations and countries)
- Creative Commons 4.0 (All declinations)

Support for other licenses such as Art Libre or WTFPL will be added in future releases.

### Instance-level moderation tools

This release includes a first set of moderation tools that will give more control
to admins about the way their instance federates with other instance and accounts on the network.
Using these tools, it's now possible to:

- Browse known accounts and domains, and associated data (storage size, software version, etc.)
- Purge data belonging to given accounts and domains
- Block or partially restrict interactions with any account or domain

All those features are usable using a brand new "moderation" permission, meaning
you can appoint one or multiple moderators to help with this task.

I'd like to thank all Mastodon contributors, because some of the these tools are heavily
inspired from what's being done in Mastodon. Thank you so much!

### Iframe widget to embed public tracks and albums [manual action required]

Funkwhale now supports embedding a lightweight audio player on external websites
for album and tracks that are available in public libraries. Important pages,
such as artist, album and track pages also include OpenGraph tags that will
enable previews on compatible apps (like sharing a Funkwhale track link on Mastodon
or Twitter).

To achieve that, we had to tweak the way Funkwhale front-end is served. You'll have
to modify your nginx configuration when upgrading to keep your instance working.

**On docker setups**, edit your `/srv/funkwhale/nginx/funkwhale.template` and replace
the `location /api/` and `location /` blocks by the following snippets:

```nginx
location / {
    include /etc/nginx/funkwhale_proxy.conf;
    # this is needed if you have file import via upload enabled
    client_max_body_size ${NGINX_MAX_BODY_SIZE};
    proxy_pass   http://funkwhale-api/;
}

location /front/ {
    alias /frontend/;
}
```

The change of configuration will be picked when restarting your nginx container.

**On non-docker setups**, edit your `/etc/nginx/sites-available/funkwhale.conf` file,
and replace the `location /api/` and `location /` blocks by the following snippets:

```nginx
location / {
    include /etc/nginx/funkwhale_proxy.conf;
    # this is needed if you have file import via upload enabled
    client_max_body_size ${NGINX_MAX_BODY_SIZE};
    proxy_pass   http://funkwhale-api/;
}

location /front/ {
    alias ${FUNKWHALE_FRONTEND_PATH}/;
}
```

Replace `${FUNKWHALE_FRONTEND_PATH}` by the corresponding variable from your .env file,
which should be `/srv/funkwhale/front/dist` by default, then reload your nginx process with
`sudo systemctl reload nginx`.

### Alternative docker deployment method

Thanks to the awesome work done by @thetarkus at https://github.com/thetarkus/docker-funkwhale,
we're now able to provide an alternative and easier Docker deployment method!

In contrast with our current, multi-container offer, this method integrates
all Funkwhale processes and services (database, redis, etc.) into a single, easier to deploy container.

Both methods will coexist in parallel, as each one has pros and cons. You can learn more
about this exciting new deployment option by visiting https://docs.funkwhale.audio/installation/docker.html!

### Automatically load .env file

On non-docker deployments, earlier versions required you to source
the config/.env file before launching any Funkwhale command, with `export $(cat config/.env | grep -v ^# | xargs)`
This led to more complex and error prone deployment / setup.

This is not the case anymore, and Funkwhale will automatically load this file if it's available.

### Delete pre 0.17 federated tracks [manual action suggested]

If you were using Funkwhale before the 0.17 release and federated with other instances,
it's possible that you still have some unplayable federated files in the database.

To purge the database of those entries, you can run the following command:

On docker setups:

```sh
docker-compose run --rm api python manage.py script delete_pre_017_federated_uploads --no-input
```

On non-docker setups:

```sh
python manage.py script delete_pre_017_federated_uploads --no-input
```

### Enable gzip compression [manual action suggested]

Gzip compression will be enabled on new instances by default
and will reduce the amount of bandwidth consumed by your instance.

If you want to benefit from gzip compression on your instance,
edit your reverse proxy virtualhost file (located at `/etc/nginx/sites-available/funkwhale.conf`) and add the following snippet
in the server block, then reload your nginx server:

```nginx
server {
    # ...

    # compression settings
    gzip on;
    gzip_comp_level    5;
    gzip_min_length    256;
    gzip_proxied       any;
    gzip_vary          on;

    gzip_types
        application/javascript
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;
    # end of compression settings
}
```

### Full changelog

Features:

- Allow embedding of albums and tracks available in public libraries via an <iframe> (#578)
- Audio transcoding is back! (#272)
- First set of instance level moderation tools (#580, !521)
- Store licensing and copyright information from file metadata, if available (#308)

Enhancements:

- Add UI elements for multi-disc albums (#631)
- Added alternative funkwhale/all-in-one docker image (#614)
- Broadcast library updates (name, description, visibility) over federation
- Based Docker image on alpine to have a smaller (and faster to build) image
- Improved front-end performance by stripping unused dependencies, reducing bundle size
  and enabling gzip compression
- Improved accessibility by using main/section/nav tags and aria-labels in most critical places (#612)
- The progress bar in the player now display loading state / buffer loading (#586)
- Added "type: funkwhale" and "funkwhale-version" in Subsonic responses (#573)
- Documented keyboard shortcuts, list is now available by pressing "h" or in the footer (#611)
- Documented which Subsonic endpoints are implemented (#575)
- Hide invitation code field during signup when it's not required (#410)
- Importer will now pick embedded images in files with OTHER type if no COVER_FRONT is present
- Improved keyboard accessibility on player, queue and various controls (#576)
- Improved performance when listing playable tracks, albums and artists
- Increased default upload limit from 30 to 100MB (#654)
- Load env file in config/.env automatically to avoid sourcing it by hand (#626)
- More resilient date parsing during audio import, will not crash anymore on
  invalid dates (#622)
- Now start radios immediately, skipping any existing tracks in queue (#585)
- Officially support connecting to a password protected redis server, with
  the redis://:password@localhost:6379/0 scheme (#640)
- Performance improvement when fetching favorites, down to a single, small http request
- Removed "Activity" page, since all the data is available on the "Browse" page (#600)
- Removed the need to specify the DJANGO_ALLOWED_HOSTS variable
- Restructured the footer, added useful links and removed unused content
- Show short entries first in search results to improve UX
- Store disc number and order tracks by disc number / position) (#507)
- Strip EXIF metadata from uploaded avatars to avoid leaking private data (#374)
- Support blind key rotation in HTTP Signatures (#658)
- Support setting a server URL in settings.json (#650)
- Updated default docker postgres version from 9.4 to 11 (#656)
- Updated lots of dependencies (especially django 2.0->2.1), and removed unused dependencies (#657)
- Improved test suite speed by reducing / disabling expensive operations (#648)

Bugfixes:

- Fixed parsing of embedded file cover for ogg files tagged with MusicBrainz (#469)
- Upgraded core dependencies to fix websocket/messaging issues and possible memory leaks (#643)
- Fix ".None" extension when downloading Flac file (#473)
- Fixed None extension when downloading an in-place imported file (#621)
- Added a script to prune pre 0.17 federated tracks (#564)
- Advertise public libraries properly in ActivityPub representations (#553)
- Allow opus file upload (#598)
- Do not display "view on MusicBrainz" button if we miss the mbid (#422)
- Do not try to create unaccent extension if it's already present (#663)
- Ensure admin links in sidebar are displayed for users with relevant permissions, and only them (#597)
- Fix broken websocket connection under Chrome browser (#589)
- Fix play button not starting playback with empty queue (#632)
- Fixed a styling inconsistency on about page when instance description was missing (#659)
- Fixed a UI discrepancy in playlist tracks count (#647)
- Fixed greyed tracks in radio builder and detail page (#637)
- Fixed inconsistencies in subsonic error responses (#616)
- Fixed incorrect icon for "next track" in player control (#613)
- Fixed malformed search string when redirecting to LyricsWiki (#608)
- Fixed missing track count on various library cards (#581)
- Fixed skipped track when appending multiple tracks to the queue under certain conditions (#209)
- Fixed wrong album/track count on artist page (#599)
- Hide unplayable/empty playlists in "Browse playlist" pages (#424)
- Initial UI render using correct language from browser (#644)
- Invalid URI for reverse proxy websocket with apache (#617)
- Properly encode Wikipedia and lyrics search urls (#470)
- Refresh profile after user settings update to avoid cache issues (#606)
- Use role=button instead of empty links for player controls (#610)

Documentation:

- Deploy documentation from the master branch instead of the develop branch to avoid inconsistencies (#642)
- Document how to find and use library id when importing files in CLI (#562)
- Fix documentation typos (#645)

## 0.17 (2018-10-07)

### Per user libraries

This release contains a big change in music management. This has a lot of impact
on how Funkwhale behaves, and you should have a look at
https://docs.funkwhale.audio/upgrading/0.17.html for information
about what changed and how to migrate.

Features:

- Per user libraries (#463, also fixes #160 and #147)
- Authentication using a LDAP directory (#194)

Enhancements:

- Add configuration option to set Musicbrainz hostname
- Add sign up link in the sidebar (#408)
- Added a library widget to display libraries associated with a track, album
  and artist (#551)
- Ensure from_activity field is not required in django's admin (#546)
- Move setting link from profile page to the sidebar (#406)
- Simplified and less error-prone nginx setup (#358)

Bugfixes:

- Do not restart current song when rordering queue, deleting tracks from queue
  or adding tracks to queue (#464)
- Fix broken icons in playlist editor (#515)
- Fixed a few untranslated strings (#559)
- Fixed split album when importing from federation (#346)
- Fixed toggle mute in volume bar does not restore previous volume level (#514)
- Fixed wrong env file URL and display bugs in deployment documentation (#520)
- Fixed wrong title in PlayButton (#435)
- Remove transparency on artist page button (#517)
- Set sane width default for ui cards and center play button (#530)
- Updated wrong icon and copy in play button dropdown (#436)

Documentation:

- Fixed wrong URLs for docker / nginx files in documentation (#537)

Other:

- Added a merge request template and more documentation about the changelog

### Using a LDAP directory to authenticate to your Funkwhale instance

Funkwhale now support LDAP as an authentication source: you can configure
your instance to delegate login to a LDAP directory, which is especially
useful when you have an existing directory and don't want to manage users
manually.

You can use this authentication backend side by side with the classic one.

Have a look at https://docs.funkwhale.audio/installation/ldap.html
for detailed instructions on how to set this up.

### Simplified nginx setup [Docker: Manual action required]

We've received a lot of user feedback regarding our installation process,
and it seems the proxy part is the one which is the most confusing and difficult.
Unfortunately, this is also the one where errors and mistakes can completely break
the application.

To make things easier for everyone, we now offer a simplified deployment
process for the reverse proxy part. This will make upgrade of the proxy configuration
significantly easier on docker deployments.

On non-docker instances, you have nothing to do.

If you have a dockerized instance, here is the upgrade path.

First, tweak your .env file:

```sh
# remove the FUNKWHALE_URL variable
# and add the next variables
FUNKWHALE_HOSTNAME=yourdomain.funkwhale
FUNKWHALE_PROTOCOL=https

# add the following variable, matching the path your app is deployed
# leaving the default should work fine if you deployed using the same
# paths as the documentation
FUNKWHALE_FRONTEND_PATH=/srv/funkwhale/front/dist
```

Then, add the following block at the end of your docker-compose.yml file:

```yaml
services:
  # existing services
  api:
    # ...
  celeryworker:
    # ...

  # new service
  nginx:
    image: nginx
    env_file:
      - .env
    environment:
      # Override those variables in your .env file if needed
      - "NGINX_MAX_BODY_SIZE=${NGINX_MAX_BODY_SIZE-100M}"
    volumes:
      - "./nginx/funkwhale.template:/etc/nginx/conf.d/funkwhale.template:ro"
      - "./nginx/funkwhale_proxy.conf:/etc/nginx/funkwhale_proxy.conf:ro"
      - "${MUSIC_DIRECTORY_SERVE_PATH-/srv/funkwhale/data/music}:${MUSIC_DIRECTORY_SERVE_PATH-/srv/funkwhale/data/music}:ro"
      - "${MEDIA_ROOT}:${MEDIA_ROOT}:ro"
      - "${STATIC_ROOT}:${STATIC_ROOT}:ro"
      - "${FUNKWHALE_FRONTEND_PATH}:/frontend:ro"
    ports:
      # override those variables in your .env file if needed
      - "${FUNKWHALE_API_IP}:${FUNKWHALE_API_PORT}:80"
    command: >
      sh -c "envsubst \"`env | awk -F = '{printf \" $$%s\", $$1}'`\"
      < /etc/nginx/conf.d/funkwhale.template
      > /etc/nginx/conf.d/default.conf
      && cat /etc/nginx/conf.d/default.conf
      && nginx -g 'daemon off;'"
    links:
      - api
```

By doing that, you'll enable a dockerized nginx that will automatically be
configured to serve your Funkwhale instance.

Download the required configuration files for the nginx container:

```{parsed-literal}
cd /srv/funkwhale
mkdir nginx
curl -L -o nginx/funkwhale.template "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/docker.nginx.template"
curl -L -o nginx/funkwhale_proxy.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/funkwhale_proxy.conf"
```

Update the funkwhale.conf configuration of your server's reverse-proxy:

```sh
# the file should match something like that, upgrade all variables
# between ${} to match the ones in your .env file,
# and your SSL configuration if you're not using let's encrypt
# The important thing is that you only have a single location block
# that proxies everything to your dockerized nginx.

sudo nano /etc/nginx/sites-enabled/funkwhale.conf
```

```nginx
upstream fw {
    # depending on your setup, you may want to update this
    server ${FUNKWHALE_API_IP}:${FUNKWHALE_API_PORT};
}
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name ${FUNKWHALE_HOSTNAME};
    location / { return 301 https://$host$request_uri; }
}
server {
    listen      443 ssl;
    listen [::]:443 ssl;
    server_name ${FUNKWHALE_HOSTNAME};

    # TLS
    ssl_protocols TLSv1.2;
    ssl_ciphers HIGH:!MEDIUM:!LOW:!aNULL:!NULL:!SHA;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_certificate     /etc/letsencrypt/live/${FUNKWHALE_HOSTNAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${FUNKWHALE_HOSTNAME}/privkey.pem;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000";

    location / {
        include /etc/nginx/funkwhale_proxy.conf;
        proxy_pass   http://fw/;
    }
}
```

Check that your configuration is valid then reload:

```sh
sudo nginx -t
sudo systemctl reload nginx
```

## 0.16.3 (2018-08-21)

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Bugfixes:

- Fixed front-end not contacting the proper path on the API (!385)

## 0.16.2 (2018-08-21)

```{warning}
**This release is broken, do not use it. Upgrade to 0.16.3 or higher instead.**
```

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Bugfixes:

- Ensure we always have a default api url set on first load to avoid displaying
  the instance picker (#490)
- Fixed CLI importer syntax error because of async reserved keyword usage
  (#494)

## 0.16.1 (2018-08-19)

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Features:

- Make funkwhale themable by loading external stylesheets (#456)

Enhancements:

- Add link to admin on "Staff member" button (#202)
- Can now add a description to radios and better radio cards (#331)
- Display track duration in track tables (#461)
- More permissive default permissions for front-end files (#388)
- Simpler configuration and toolchain for the front-end using vue-cli (!375)
- Use Howler to manage audio instead of our own dirty/untested code (#392)

Bugfixes:

- Fix alignment issue on top bar in Admin tabs (#395)
- Fix Apache2 permission issue preventing `/media` folder from being served
  correctly (#389)
- Fix loading on browse page lists causing them to go down, and dimming over
  the top bar (#468)
- Fixed (again): administration section not showing up in sidebar after login
  (#245)
- Fixed audio mimetype not showing up on track detail and list (#459)
- Fixed broken audio playback on Chrome and invisible volume control (#390)
- Fixed broken federation import on big imports due to missing transaction
  logic (#397)
- Fixed crash on artist pages when no cover is available (#457)
- Fixed favorited status of tracks not appearing in interface (#398)
- Fixed invitation code not prefilled in form when accessing invitation link
  (#476)
- Fixed typos in scheduled tasks configuration (#487)
- Removed release date error in case of empty date (#478)
- Removed white on white artist button on hover, on Album page (#393)
- Smarter date parsing during import by replacing arrow with pendulum (#376)
- Display public playlists properly for anonymous users (#488)

i18n:

- Added portuguese, spanish and german translations

### Custom themes for Funkwhale

If you ever wanted to give a custom look and feel to your instance, this is now possible.

Check https://docs.funkwhale.audio/configuration.html#theming if you want to know more!

### Fix Apache2 configuration file for media block [Manual action required]

The permission scope on the current Apache2 configuration file is too narrow, preventing thumbnails from being served.

On Apache2 setups, you have to replace the following line:

```apache
<Directory /srv/funkwhale/data/media/albums>
```

with:

```apache
<Directory /srv/funkwhale/data/media>
```

You can now restart your server:

```sh
sudo systemctl restart apache2
```

## 0.16 (2018-07-22)

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Features:

- Complete redesign of the library home and playlist pages (#284)
- Expose ActivityPub actors for users (#317)
- Implemented a basic but functional Github-like search on federated tracks
  list (#344)
- Internationalized interface as well as translations for Arabic, French,
  Esperanto, Italian, Occitan, Polish, Portuguese and Swedish (#161, #167)
- Users can now upload an avatar in their settings page (#257)

Enhancements:

- Added feedback when creating/updating radio (#302)
- Apply restrictions to username characters during signup
- Autoselect best language based on browser configuration (#386)
- Can now order tracks on federated track list (#326)
- Can now relaunch pending import jobs from the web interface (#323)
- Ensure we do not display pagination on single pages (#334)
- Ensure we have sane defaults for MEDIA_ROOT, STATIC_ROOT and
  MUSIC_DIRECTORY_PATH in the deployment .env file (#350)
- Make some space for the volume slider to allow precise control (#318)
- Removed django-cacheops dependency
- Store track artist and album artist separately (#237) Better handling of
  tracks with a different artist than the album artist
- The navigation bar of Library is now fixed (#375)
- Use thumbnails for avatars and covers to reduce bandwidth

Bugfixes:

- Ensure 750 permissions on CI artifacts (#332)
- Ensure images are not cropped in queue (#337)
- Ensure we do not import artists with empty names (#351)
- Fix notifications not closing when clicking on the cross (#366)
- Fix the most annoying offset in the whole fediverse (#369)
- Fixed persistent message in playlist modal (#304)
- Fixed unfiltered results in favorites API (#384)
- Raise a warning instead of crashing when getting a broken path in file import
  (#138)
- Remove parallelization of uploads during import to avoid crashing small
  servers (#382)
- Subsonic API login is now case insensitive (#339)
- Validate Date header in HTTP Signatures (#328)

Documentation:

- Added troubleshotting and technical overview documentation (#256)
- Arch Linux installation steps
- Document that users can use Ultrasonic on Android (#316)
- Fixed a couple of typos
- Some cosmetic improvements to the doc

i18n:

- Arabic translation (!302)
- Polish translation (!304)

### Library home and playlist page overhaul

The library home page have been completely redesigned to include:

- other users activity (listenings, playlists and favorites)
- recently imported albums

We think this new version showcases more music in a more useful way, let us know
what you think about it!

The playlist page have been updated as well.

### Internationalized interface

After months of work, we're proud to announce our interface is now ready
for internationalization.

Translators have already started the work of translating Funkwhale in 8 different languages,
and we're ready to add more as needed.

You can easily get involved at https://translate.funkwhale.audio/engage/funkwhale/

### Better handling of tracks with a different artist than the album artist

Some tracks involve a different artist than the album artist (e.g. a featuring)
and Funkwhale has been known to do weird things when importing such tracks, resulting
in albums that contained a single track, for instance.

The situation should be improved with this release, as Funkwhale is now able to
store separately the track and album artist, and display it properly in the interface.

### Users now have an ActivityPub Actor [Manual action required]

In the process of implementing federation for user activity such as listening
history, we are now making user profiles (a.k.a. ActivityPub actors) available through federation.

This does not means the federation is working, but this is a needed step to implement it.

Those profiles will be created automatically for new users, but you have to run a command
to create them for existing users.

On docker setups:

```sh
docker-compose run --rm api python manage.py script create_actors --no-input
```

On non-docker setups:

```sh
python manage.py script create_actors --no-input
```

This should only take a few seconds to run. It is safe to interrupt the process or rerun it multiple times.

### Image thumbnails [Manual action required]

To reduce bandwidth usage on slow or limited connexions and improve performance
in general, we now use smaller images in the front-end. For instance, if you have
an album cover with a 1000x1000 pixel size, we will create smaller
versions of this image (50x50, 200x200, 400x400) and reference those resized version
when we don't actually need the original image.

Thumbnail will be created automatically for new objects, however, you have
to launch a manual command to deal with existing ones.

On docker setups:

```sh
docker-compose run --rm api python manage.py script create_image_variations --no-input
```

On non-docker setups:

```sh
python manage.py script create_image_variations --no-input
```

This should be quite fast but may take up to a few minutes depending on the number
of albums you have in database. It is safe to interrupt the process or rerun it multiple times.

### Improved search on federated tracks list

Having a powerful but easy-to-use search is important but difficult to achieve, especially
if you do not want to have a real complex search interface.

Github does a pretty good job with that, using a structured but simple query system
(See https://help.github.com/articles/searching-issues-and-pull-requests/#search-only-issues-or-pull-requests).

This release implements a limited but working subset of this query system. You can use it only on the federated
tracks list (/manage/federation/tracks) at the moment, but depending on feedback it will be rolled-out on other pages as well.

This is the type of query you can run:

- `hello world`: search for "hello" and "world" in all the available fields
- `hello in:artist` search for results where artist name is "hello"
- `spring in:artist,album` search for results where artist name or album title contain "spring"
- `artist:hello` search for results where artist name equals "hello"
- `artist:"System of a Down" domain:instance.funkwhale` search for results where artist name equals "System of a Down" and inside "instance.funkwhale" library

### Ensure `MEDIA_ROOT`, `STATIC_ROOT` and `MUSIC_DIRECTORY_*` are set explicitly [Manual action required]

In our default .env file, MEDIA_ROOT and STATIC_ROOT were commented by default, causing
some deployment issues on non-docker setups when people forgot to uncomment them.

From now on, those variables are uncommented, and will also be used on docker setups
to mount the volumes automatically in the docker-compose.yml file. This has been a source
of headache as well in some deployments, where you had to update both the .env file and
the compose file.

This also applies to in-place paths (MUSIC_DIRECTORY_PATH and MUSIC_DIRECTORY_SERVE_PATH),
whose values are now used directly to set up the proper Docker volumes.

This will only affect new deployments though. If you want to benefit from this on an
existing instance, do a backup of your `.env` and `docker-compose.yml` files and apply the following changes:

- Ensure `MEDIA_ROOT` is uncommented in your .env file and match the absolute path where media files are stored
  on your host (`/srv/funkwhale/data/media` by default)
- Ensure `STATIC_ROOT` is uncommented in your .env file and match the absolute path where static files are stored
  on your host (`/srv/funkwhale/data/static` by default)
- If you use in-place import:
  - Ensure MUSIC_DIRECTORY_PATH is uncommented and set to `/music`
  - Ensure MUSIC_DIRECTORY_SERVE_PATH is uncommented and set to the absolute path on your host were your music files
    are stored (`/srv/funkwhale/data/music` by default)
- Edit your docker-compose.yml file to reflect the changes:
  - Search for volumes (there should be two occurrences) that contains `/app/funkwhale_api/media` on the right side, and
    replace the whole line with `- "${MEDIA_ROOT}:${MEDIA_ROOT}"`
  - Search for a volume that contains `/app/staticfiles` on the right side, and
    replace the whole line with `- "${STATIC_ROOT}:${STATIC_ROOT}"`
  - If you use in-place import, search for volumes (there should be two occurrences) that contains `/music:ro` on the right side, and
    replace the whole line with `- "${MUSIC_DIRECTORY_SERVE_PATH}:${MUSIC_DIRECTORY_PATH}:ro"`

In the end, the `volumes` directives of your containers should look like that:

```yaml
services:
  # ...
  celeryworker:
    volumes:
      - "${MUSIC_DIRECTORY_SERVE_PATH}:${MUSIC_DIRECTORY_PATH}:ro"
      - "${MEDIA_ROOT}:${MEDIA_ROOT}"
  # ...
  api:
    volumes:
      - "${MUSIC_DIRECTORY_SERVE_PATH}:${MUSIC_DIRECTORY_PATH}:ro"
      - "${MEDIA_ROOT}:${MEDIA_ROOT}"
      - "${STATIC_ROOT}:${STATIC_ROOT}"
      - ./front/dist:/frontend
  # ...
```

### Removed Cacheops dependency

We removed one of our dependency named django-cacheops. It was unly used in a few places,
and not playing nice with other dependencies.

You can safely remove this dependency in your environment with `pip uninstall django-cacheops` if you're
not using docker.

You can also safely remove any `CACHEOPS_ENABLED` setting from your environment file.

## 0.15 (2018-06-24)

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Features:

- Added admin interface to manage import requests (#190)
- Added replace flag during import to replace already present tracks with a new
  version of their track file (#222)
- Funkwhale's front-end can now point to any instance (#327) Removed front-end
  and back-end coupling
- Management interface for users (#212)
- New invite system (#248) New invite system

Enhancements:

- Added "TV" to the list of highlighted words during YouTube import (#154)
- Command line import now accepts unlimited args (#242)

Bugfixes:

- Expose track files date in manage API (#307)
- Fixed current track restart/hiccup when shuffling queue, deleting track from
  queue or reordering (#310)
- Include user's current private playlists on playlist list (#302)
- Remove link to generic radios, since they don't have detail pages (#324)

Documentation:

- Document that Funkwhale may be installed with YunoHost (#325)
- Documented a saner layout with symlinks for in-place imports (#254)
- Upgrade documentation now use the correct user on non-docker setups (#265)

### Invite system

On closed instances, it has always been a little bit painful to create accounts
by hand for new users. This release solve that by adding invitations.

You can generate invitation codes via the "users" admin interface (you'll find a
link in the sidebar). Those codes are valid for 14 days, and can be used once
to create a new account on the instance, even if registrations are closed.

By default, we generate a random code for invitations, but you can also use custom codes
if you need to print them or make them fancier ;)

Invitations generation and management requires the "settings" permission.

### Removed front-end and back-end coupling

Even though Funkwhale's front-end has always been a Single Page Application,
talking to an API, it was only able to talk to an API on the same domain.

There was no real technical justification behind this (only laziness), and it was
also blocking interesting use cases:

- Use multiple customized versions of the front-end with the same instance
- Use a customized version of the front-end with multiple instances
- Use a locally hosted front-end with a remote API, which is especially useful in development

From now on, Funkwhale's front-end can connect to any Funkwhale server. You can
change the server you are connecting to in the footer.

Fixing this also unlocked a really interesting feature in our development/review workflow:
by leveraging Gitlab CI and review apps, we are now able to deploy automatically live versions of
a merge request, making it possible for anyone to review front-end changes easily, without
the need to install a local environment.

## 0.14.2 (2018-06-16)

```{warning}
This release contains a fix for a permission issue. You should upgrade
as soon as possible. Read the changelog below for more details.
```

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Enhancements:

- Added feedback on shuffle button (#262)
- Added multiple warnings in the documentation that you should never run
  makemigrations yourself (#291)
- Album cover served in http (#264)
- Apache2 reverse proxy now supports websockets (tested with Apache 2.4.25)
  (!252)
- Display file size in human format during file upload (#289)
- Switch from BSD-3 licence to AGPL-3 licence (#280)

Bugfixes:

- Ensure radios can only be edited and deleted by their owners (#311)
- Fixed admin menu not showing after login (#245)
- Fixed broken pagination in Subsonic API (#295)
- Fixed duplicated websocket connection on timeline (#287)

Documentation:

- Improved documentation about in-place imports setup (#298)

Other:

- Added Black and flake8 checks in CI to ensure consistent code styling and
  formatting (#297)
- Added bug and feature issue templates (#299)

### Permission issues on radios

Because of an error in the way we checked user permissions on radios,
public radios could be deleted by any logged-in user, even if they were not
the owner of the radio.

We recommend instances owners to upgrade as fast as possible to avoid any abuse
and data loss.

### Funkwhale is now licenced under AGPL-3

Following the recent switch made by PixelFed
(https://github.com/dansup/pixelfed/issues/143), we decided along with
the community to relicence Funkwhale under the AGPL-3 licence. We did this
switch for various reasons:

- This is better aligned with other fediverse software
- It prohibits anyone to distribute closed-source and proprietary forks of Funkwhale

As end users and instance owners, this does not change anything. You can
continue to use Funkwhale exactly as you did before :)

### Apache support for websocket

Up until now, our Apache2 configuration was not working with websockets. This is now
solved by adding this at the beginning of your Apache2 configuration file:

```apache
Define funkwhale-api-ws ws://localhost:5000
```

And this, before the "/api" block:

```apache
# Activating WebSockets
ProxyPass "/api/v1/instance/activity" ${funkwhale-api-ws}/api/v1/instance/activity
```

Websockets may not be supported in older versions of Apache2. Be sure to upgrade to the latest version available.

### Serving album covers in https (Apache2 proxy)

Two issues are addressed here. The first one was about Django replying with
mixed content (http) when queried for covers. Setting up the `X-Forwarded-Proto`
allows Django to know that the client is using https, and that the reply must
be https as well.

Second issue was a problem of permission causing Apache a denied access to
album cover folder. It is solved by adding another block for this path in
the Apache configuration file for funkwhale.

Here is how to modify your `funkwhale.conf` apache2 configuration:

```apache
<VirtualHost *:443>
  # ...
  #Add this new line
  RequestHeader set X-Forwarded-Proto "https"
  # ...
  # Add this new block below the other <Directory/> blocks
  # replace /srv/funkwhale/data/media with the path to your media directory
  # if you're not using the standard layout.
  <Directory /srv/funkwhale/data/media/albums>
    Options FollowSymLinks
    AllowOverride None
    Require all granted
  </Directory>
  # ...
</VirtualHost>
```

### About the makemigrations warning

You may sometimes get the following warning while applying migrations:

```
"Your models have changes that are not yet reflected in a migration, and so won't be applied."
```

This is a warning, not an error, and it can be safely ignored.
Never run the `makemigrations` command yourself.

## 0.14.1 (2018-06-06)

Upgrade instructions are available at https://docs.funkwhale.audio/upgrading.html

Enhancements:

- Display server version in the footer (#270)
- fix_track_files will now update files with bad mimetype (and not only the one
  with no mimetype) (#273)
- Huge performance boost (~x5 to x7) during CLI import that queries MusicBrainz
  (#288)
- Removed alpha-state transcoding support (#271)

Bugfixes:

- Broken logging statement during import error (#274)
- Broken search bar on library home (#278)
- Do not crash when importing track with an artist that do not match the
  release artist (#237)
- Do not crash when tag contains multiple uuids with a / separator (#267)
- Ensure we do not store bad mimetypes (such as application/x-empty) (#266)
- Fix broken "play all" button that played only 25 tracks (#281)
- Fixed broken track download modal (overflow and wrong URL) (#239)
- Removed hardcoded size limit in file upload widget (#275)

Documentation:

- Added warning about \_protected/music location in nginx configuration (#247)

### Removed alpha-state transcoding (#271)

A few months ago, a basic transcoding feature was implemented. Due to the way
this feature was designed, it was slow, CPU intensive on the server side,
and very tightly coupled to the reverse-proxy configuration, preventing
it to work Apache2, for instance. It was also not compatible with Subsonic clients.

Based on that, we're currently removing support for transcoding
**in its current state**. The work on a better designed transcoding feature
can be tracked in https://dev.funkwhale.audio/funkwhale/funkwhale/issues/272.

You don't have to do anything on your side, but you may want to remove
the now obsolete configuration from your reverse proxy file (nginx only):

```nginx
# Remove those blocks:

# transcode cache
proxy_cache_path /tmp/funkwhale-transcode levels=1:2 keys_zone=transcode:10m max_size=1g inactive=7d;

# Transcoding logic and caching
location = /transcode-auth {
    include /etc/nginx/funkwhale_proxy.conf;
    # needed so we can authenticate transcode requests, but still
    # cache the result
    internal;
    set $query '';
    # ensure we actually pass the jwt to the underlytin auth url
    if ($request_uri ~* "[^\?]+\?(.*)$") {
        set $query $1;
    }
    proxy_pass http://funkwhale-api/api/v1/trackfiles/viewable/?$query;
    proxy_pass_request_body off;
    proxy_set_header        Content-Length "";
}

location /api/v1/trackfiles/transcode/ {
    include /etc/nginx/funkwhale_proxy.conf;
    # this block deals with authenticating and caching transcoding
    # requests. Caching is heavily recommended as transcoding
    # is a CPU intensive process.
    auth_request /transcode-auth;
    if ($args ~ (.*)jwt=[^&]*(.*)) {
        set $cleaned_args $1$2;
    }
    proxy_cache_key "$scheme$request_method$host$uri$is_args$cleaned_args";
    proxy_cache transcode;
    proxy_cache_valid 200 7d;
    proxy_ignore_headers "Set-Cookie";
    proxy_hide_header "Set-Cookie";
    add_header X-Cache-Status $upstream_cache_status;
    proxy_pass   http://funkwhale-api;
}
# end of transcoding logic
```

## 0.14 (2018-06-02)

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Features:

- Admins can now configure default permissions that will be granted to all
  registered users (#236)
- Files management interface for users with "library" permission (#223)
- New action table component for quick and efficient batch actions (#228) This
  is implemented on the federated tracks pages, but will be included in other
  pages as well depending on the feedback.

Enhancements:

- Added a new "upload" permission that allows user to launch import and view
  their own imports (#230)
- Added Support for OggTheora in import.
- Autoremove media files on model instance deletion (#241)
- Can now import a whole remote library at once thanks to new Action Table
  component (#164)
- Can now use album covers from flac/mp3 metadata and separate file in track
  directory (#219)
- Implemented getCovertArt in Subsonic API to serve album covers (#258)
- Implemented scrobble endpoint of subsonic API, listenings are now tracked
  correctly from third party apps that use this endpoint (#260)
- Retructured music API to increase performance and remove useless endpoints
  (#224)

Bugfixes:

- Consistent constraints/checks for URL size (#207)
- Display proper total number of tracks on radio detail (#225)
- Do not crash on flac import if musicbrainz tags are missing (#214)
- Empty save button in radio builder (#226)
- Ensure anonymous users can use the app if the instance is configured
  accordingly (#229)
- Ensure inactive users cannot get auth tokens (#218) This was already the case
  bug we missed some checks
- File-upload import now supports Flac files (#213)
- File-upload importer should now work properly, assuming files are tagged
  (#106)
- Fixed a few broken translations strings (#227)
- Fixed broken ordering in front-end lists (#179)
- Fixed ignored page_size parameter on artist and favorites list (#240)
- Read ID3Tag Tracknumber from TRCK (#220)
- We now fetch album covers regardless of the import methods (#231)

Documentation:

- Added missing subsonic configuration block in deployment vhost files (#249)
- Moved upgrade doc under install doc in TOC (#251)

Other:

- Removed acoustid support, as the integration was buggy and error-prone (#106)

### Files management interface

This is the first bit of an ongoing work that will span several releases, to
bring more powerful library management features to Funkwhale. This iteration
includes a basic file management interface where users with the "library"
permission can list and search available files, order them using
various criteria (size, bitrate, duration...) and delete them.

### New "upload" permission

This new permission is helpful if you want to give upload/import rights
to some users, but don't want them to be able to manage the library as a whole:
although there are no controls yet for managing library in the fron-end,
subsequent release will introduce management interfaces for artists, files,
etc.

Because of that, users with the "library" permission will have much more power,
and will also be able to remove content from the platform. On the other hand,
users with the "upload" permission will only have the ability to add new
content.

Also, this release also includes a new feature called "default permissions":
those are permissions that are granted to every users on the platform.
On public/open instances, this will play well with the "upload" permission
since everyone will be able to contribute to the instance library without
an admin giving the permission to every single user.

### Smarter album cover importer

In earlier versions, covers where only imported when launching a YouTube import.
Starting from this release, covers will be imported regardless of the import mode
(file upload, youtube-dl, CLI, in-place...). Funkwhale will look for covers
in the following order:

1. In the imported file itself (FLAC/MP3 only)
2. In a cover.jpg or cover.png in the file directory
3. By fetching cover art from Musibrainz, assuming the file is tagged correctly

This will only work for newly imported tracks and albums though. In the future,
we may offer an option to refetch album covers from the interface, but in the
meantime, you can use the following snippet:

```python
# Store this in /tmp/update_albums.py
from funkwhale_api.music.models import Album, TrackFile
from funkwhale_api.music.tasks import update_album_cover

albums_without_covers = Album.objects.filter(cover='')
total = albums_without_covers.count()
print('Found {} albums without cover'.format(total))
for i, album in enumerate(albums_without_covers.iterator()):
    print('[{}/{}] Fetching cover for {}...'.format(i+1, total, album.title))
    f = TrackFile.objects.filter(track__album=album).filter(source__startswith='file://').first()
    update_album_cover(album, track_file=f)
```

Then launch it:

```sh
# docker setups
cat /tmp/update_albums.py | docker-compose run --rm api python manage.py shell -i python

# non-docker setups
source /srv/funkwhale/load_env
source /srv/funkwhale/virtualenv/bin/activate
cat /tmp/update_albums.py | python manage.py shell -i python

# cleanup
rm /tmp/update_albums.py
```

```{note}
Depending on your number of albums, the previous snippet may take some time
to execute. You can interrupt it at any time using ctrl-c and relaunch it later,
as it's idempotent.
```

### Music API changes

This release includes an API break. Even though the API is advertised
as unstable, and not documented, here is a brief explanation of the change in
case you are using the API in a client or in a script. Summary of the changes:

- `/api/v1/artists` does not includes a list of tracks anymore. It was to heavy
  to return all of this data all the time. You can get all tracks for an
  artist using `/api/v1/tracks?artist=artist_id`
- Additionally, `/api/v1/tracks` now support an `album` filter to filter
  tracks matching an album
- `/api/v1/artists/search`, `/api/v1/albums/search` and `/api/v1/tracks/search`
  endpoints are removed. Use `/api/v1/{artists|albums|tracks}/?q=yourquery`
  instead. It's also more powerful, since you can combine search with other
  filters and ordering options.
- `/api/v1/requests/import-requests/search` endpoint is removed as well.
  Use `/api/v1/requests/import-requests/?q=yourquery`
  instead. It's also more powerful, since you can combine search with other
  filters and ordering options.

Of course, the front-end was updated to work with the new API, so this should
not impact end-users in any way, apart from slight performance gains.

```{note}
The API is still not stable and may evolve again in the future. API freeze
will come at a later point.
```

### Flac files imports via upload

You have nothing to do to benefit from this, however, since Flac files
tend to be a lot bigger than other files, you may want to increase the
`client_max_body_size` value in your Nginx configuration if you plan
to upload flac files.

### Missing subsonic configuration block in vhost files

Because of a missing block in the sample Nginx and Apache configurations,
instances that were deployed after the 0.13 release are likely to be unable
to answer to Subsonic clients (the missing bits were properly documented
in the changelog).

Ensure you have the following snippets in your Nginx or Apache configuration
if you plan to use the Subsonic API.

Nginx:

```nginx
location /rest/ {
    include /etc/nginx/funkwhale_proxy.conf;
    proxy_pass   http://funkwhale-api/api/subsonic/rest/;
}
```

Apache2:

```apache
<Location "/rest">
    ProxyPass ${funkwhale-api}/api/subsonic/rest
    ProxyPassReverse ${funkwhale-api}/api/subsonic/rest
  </Location>
```

## 0.13 (2018-05-19)

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Features:

- Can now import and play flac files (#157)
- Simpler permission system (#152)
- Store file length, size and bitrate (#195)
- We now have a brand new instance settings interface in the front-end (#206)

Enhancements:

- Disabled browsable HTML API in production (#205)
- Instances can now indicate on the nodeinfo endpoint if they want to remain
  private (#200)

Bugfixes:

- .well-known/nodeinfo endpoint can now answer to request with Accept:
  application/json (#197)
- Fixed escaping issue of track name in playlist modal (#201)
- Fixed missing dot when downloading file (#204)
- In-place imported tracks with non-ascii characters don't break reverse-proxy
  serving (#196)
- Removed Python 3.6 dependency (secrets module) (#198)
- Uplayable tracks are now properly disabled in the interface (#199)

### Instance settings interface

Prior to this release, the only way to update instance settings (such as
instance description, signup policy, federation configuration, etc.) was using
the admin interface provided by Django (the back-end framework which power the API).

This interface worked, but was not really-user friendly and intuitive.

Starting from this release, we now offer a dedicated interface directly
in the front-end. You can view and edit all your instance settings from here,
assuming you have the required permissions.

This interface is available at `/manage/settings` and via link in the sidebar.

### Storage of bitrate, size and length in database

Starting with this release, when importing files, Funkwhale will store
additional information about audio files:

- Bitrate
- Size (in bytes)
- Duration

This change is not retroactive, meaning already imported files will lack those
information. The interface and API should work as before in such case, however,
we offer a command to deal with legacy files and populate the missing values.

On docker setups:

```sh
docker-compose run --rm api python manage.py fix_track_files
```

On non-docker setups:

```sh
# from your activated virtualenv
python manage.py fix_track_files
```

```{note}
The execution time for this command is proportional to the number of
audio files stored on your instance. This is because we need to read the
files from disk to fetch the data. You can run it in the background
while Funkwhale is up.

It's also safe to interrupt this command and rerun it at a later point, or run
it multiple times.

Use the --dry-run flag to check how many files would be impacted.
```

### Simpler permission system

Starting from this release, the permission system is much simpler. Up until now,
we were using Django's built-in permission system, which was working, but also
quite complex to deal with.

The new implementation relies on simpler logic, which will make integration
on the front-end in upcoming releases faster and easier.

If you have manually given permissions to users on your instance,
you can migrate those to the new system.

On docker setups:

```sh
docker-compose run --rm api python manage.py script django_permissions_to_user_permissions --no-input
```

On non-docker setups:

```sh
# in your virtualenv
python api/manage.py script django_permissions_to_user_permissions --no-input
```

There is still no dedicated interface to manage user permissions, but you
can use the admin interface at `/api/admin/users/user/` for that purpose in
the meantime.

## 0.12 (2018-05-09)

Upgrade instructions are available at
https://docs.funkwhale.audio/upgrading.html

Features:

- Subsonic API implementation to offer compatibility with existing clients such
  as DSub (#75)
- Use nodeinfo standard for publishing instance information (#192)

Enhancements:

- Play button now play tracks immediately instead of appending them to the
  queue (#99, #156)

Bugfixes:

- Fix broken federated import (#193)

Documentation:

- Up-to-date documentation for upgrading front-end files on docker setup (#132)

### Subsonic API

This release implements some core parts of the Subsonic API, which is widely
deployed in various projects and supported by numerous clients.

By offering this API in Funkwhale, we make it possible to access the instance
library and listen to the music without from existing Subsonic clients, and
without developing our own alternative clients for each and every platform.

Most advanced Subsonic clients support offline caching of music files,
playlist management and search, which makes them well-suited for nomadic use.

Please see [our list of supported apps](https://funkwhale.audio/apps)
for more information about supported clients and user instructions.

At the instance-level, the Subsonic API is enabled by default, but require
and additional endpoint to be added in you reverse-proxy configuration.

On nginx, add the following block:

```nginx
location /rest/ {
    include /etc/nginx/funkwhale_proxy.conf;
    proxy_pass   http://funkwhale-api/api/subsonic/rest/;
}
```

On Apache, add the following block:

```apache
<Location "/rest">
    ProxyPass ${funkwhale-api}/api/subsonic/rest
    ProxyPassReverse ${funkwhale-api}/api/subsonic/rest
</Location>
```

The Subsonic can be disabled at the instance level from the django admin.

```{note}
Because of Subsonic's API design which assumes cleartext storing of
user passwords, we chose to have a dedicated, separate password
for that purpose. Users can generate this password from their
settings page in the web client.
```

### Nodeinfo standard for instance information and stats

```{warning}
The ``/api/v1/instance/stats/`` endpoint which was used to display
instance data in the about page is removed in favor of the new
``/api/v1/instance/nodeinfo/2.0/`` endpoint.
```

In earlier version, we where using a custom endpoint and format for
our instance information and statistics. While this was working,
this was not compatible with anything else on the fediverse.

We now offer a nodeinfo 2.0 endpoint which provides, in a single place,
all the instance information such as library and user activity statistics,
public instance settings (description, registration and federation status, etc.).

We offer two settings to manage nodeinfo in your Funkwhale instance:

1. One setting to completely disable nodeinfo, but this is not recommended
   as the exposed data may be needed to make some parts of the front-end
   work (especially the about page).
2. One setting to disable only usage and library statistics in the nodeinfo
   endpoint. This is useful if you want the nodeinfo endpoint to work,
   but don't feel comfortable sharing aggregated statistics about your library
   and user activity.

To make your instance fully compatible with the nodeinfo protocol, you need to
to edit your nginx configuration file:

```nginx
# before
# ...
location /.well-known/webfinger {
    include /etc/nginx/funkwhale_proxy.conf;
    proxy_pass   http://funkwhale-api/.well-known/webfinger;
}
# ...

# after
# ...
location /.well-known/ {
    include /etc/nginx/funkwhale_proxy.conf;
    proxy_pass   http://funkwhale-api/.well-known/;
}
# ...
```

You can do the same if you use apache:

```apache
# before
# ...
<Location "/.well-known/webfinger">
  ProxyPass ${funkwhale-api}/.well-known/webfinger
  ProxyPassReverse ${funkwhale-api}/.well-known/webfinger
</Location>
# ...

# after
# ...
<Location "/.well-known/">
  ProxyPass ${funkwhale-api}/.well-known/
  ProxyPassReverse ${funkwhale-api}/.well-known/
</Location>
# ...
```

This will ensure all well-known endpoints are proxied to funkwhale, and
not just webfinger one.

Links:

- About nodeinfo: https://github.com/jhass/nodeinfo

## 0.11 (2018-05-06)

Upgrade instructions are available at https://docs.funkwhale.audio/upgrading.html

Special thanks for this release go to @renon:matrix.org (@Hazmo on Gitlab)
for bringing Apache2 support to Funkwhale and contributing on other issues.
Thank you!

Features:

- Funkwhale now works behind an Apache2 reverse proxy (!165)
  check out the brand new documentation at https://docs.funkwhale.audio/installation/index.html#apache2
  if you want to try it!
- Users can now request password reset by email, assuming a SMTP server was
  correctly configured (#187)

Enhancements:

- Added a fix_track_files command to run checks and fixes against library
  (#183)
- Avoid fetching Actor object on every request authentication
- Can now relaunch errored jobs and batches (#176)
- List pending requests by default, added a status filter for requests (#109)
- More structured menus in sidebar, added labels with notifications
- Sample virtual-host file for Apache2 reverse-proxy (!165)
- Store high-level settings (such as federation or auth-related ones) in
  database (#186)

Bugfixes:

- Ensure in place imported files get a proper mimetype (#183)
- Federation cache suppression is now simpler and also deletes orphaned files
  (#189)
- Fixed small UI glitches/bugs in federation tabs (#184)
- X-sendfile not working with in place import (#182)

Documentation:

- Added a documentation area for third-party projects (#180)
- Added documentation for optimizing Funkwhale and reduce its memory footprint.
- Document that the database should use an utf-8 encoding (#185)
- Foundations for API documentation with Swagger (#178)

### Database storage for high-level settings

Due to the work done in #186, the following environment variables have been
deprecated:

- FEDERATION_ENABLED
- FEDERATION_COLLECTION_PAGE_SIZE
- FEDERATION_MUSIC_NEEDS_APPROVAL
- FEDERATION_ACTOR_FETCH_DELAY
- PLAYLISTS_MAX_TRACKS
- API_AUTHENTICATION_REQUIRED

Configuration for this settings has been moved to database, as it will provide
a better user-experience, by allowing you to edit these values on-the-fly,
without restarting Funkwhale processes.

You can leave those environment variables in your .env file for now, as the
values will be used to populate the database entries. We'll make a proper
announcement when the variables won't be used anymore.

Please browse https://docs.funkwhale.audio/configuration.html#instance-settings
for more information about instance configuration using the web interface.

### System emails

Starting from this release, Funkwhale will send two types
of emails:

- Email confirmation emails, to ensure a user's email is valid
- Password reset emails, enabling user to reset their password without an admin's intervention

Email sending is disabled by default, as it requires additional configuration.
In this mode, emails are simply outputted on stdout.

If you want to actually send those emails to your users, you should edit your
.env file and tweak the `EMAIL_CONFIG` variable. See :data:`EMAIL_CONFIG <config.settings.common.EMAIL_CONFIG>`
for more details.

```{note}
As a result of these changes, the ``DJANGO_EMAIL_BACKEND`` variable,
which was not documented, has no effect anymore. You can safely remove it from
your .env file if it is set.
```

### Proxy headers for non-docker deployments

For non-docker deployments, add `--proxy-headers` at the end of the `daphne`
command in :file:`/etc/systemd/system/funkwhale-server.service`.

This will ensure the application receive the correct IP address from the client
and not the proxy's one.

## 0.10 (2018-04-23)

Features:

- Can now import files in-place from the CLI importer (#155)

Enhancements:

- Avoid downloading audio files multiple times from remote libraries (#163)
- Better file import performance and error handling (#144)
- Import job and batch API and front-end have been improved with better
  performance, pagination and additional filters (#171)
- Increased max_length on TrackFile.source, this will help when importing files
  with a really long path (#142)
- Player is back in Queue tab (#150)

Bugfixes:

- Fail graciously when AP representation includes a null_value for mediaType
- Fix sidebar tabs not showing under small resolution under Chrome (#173)
- Fixed broken login due to badly configured Axios (#172)
- Fixed broken playlist modal after login (#155)
- Fixed queue reorder or track deletion restarting currently playing track
  (#151)
- Radio will now append new track if you delete the last track in queue (#145)
- Reset all sensitive front-end data on logout (#124)
- Typos/not showing text due to i18n work (#175)

Documentation:

- Better documentation for hardware requirements and memory usage (#165)

### In-place import

This release includes in-place imports for the CLI import. This means you can
load gigabytes of music into funkwhale without worrying about about Funkwhale
copying those music files in its internal storage and eating your disk space.

[This new feature is documented here](https://docs.funkwhale.audio/importing-music.html#in-place-import)
and require additional configuration to ensure funkwhale and your webserver can
serve those files properly.

**Non-docker users:**

Assuming your music is stored in `/srv/funkwhale/data/music`, add the following
block to your nginx configuration:

```nginx
location /_protected/music {
    internal;
    alias   /srv/funkwhale/data/music;
}
```

And the following to your .env file:

```sh
MUSIC_DIRECTORY_PATH=/srv/funkwhale/data/music
```

**Docker users:**

Assuming your music is stored in `/srv/funkwhale/data/music`, add the following
block to your nginx configuration:

```nginx
location /_protected/music {
    internal;
    alias   /srv/funkwhale/data/music;
}
```

Assuming you have the following volume directive in your `docker-compose.yml`
(it's the default): `/srv/funkwhale/data/music:/music:ro`, then add
the following to your .env file:

```sh
# this is the path in the container
MUSIC_DIRECTORY_PATH=/music
# this is the path on the host
MUSIC_DIRECTORY_SERVE_PATH=/srv/funkwhale/data/music
```

## 0.9.1 (2018-04-17)

Bugfixes:

- Allow null values for musicbrainz_id in Audio ActivityPub representation
- Fixed broken permission check on library scanning and too aggressive page
  validation

## 0.9 (2018-04-17)

Features:

- Add internationalization support (#5)
- Can now follow and import music from remote libraries (#136, #137)

Enhancements:

- Added a i18n-extract yarn script to extract strings to PO files (#162)
- User admin now includes signup and last login dates (#148)
- We now use a proper user agent including instance version and url during
  outgoing requests

### Federation is here!

This is for real this time, and includes:

- Following other Funkwhale libraries
- Importing tracks from remote libraries (tracks are hotlinked, and only cached for a short amount of time)
- Searching across federated catalogs

Note that by default, federation is opt-in, on a per-instance basis:
instances will request access to your catalog, and you can accept or refuse
those requests. You can also revoke the access at any time.

Documentation was updated with relevant instructions to use and benefit
from this new feature: https://docs.funkwhale.audio/federation.html

### Preparing internationalization

Funkwhale's front-end as always been english-only, and this is a barrier
to new users. The work make Funkwhale's interface translatable was started
in this release by Baptiste. Although nothing is translated yet,
this release includes behind the stage changes that will make it possible in
the near future.

Many thank to Baptiste for the hard work and for figuring out a proper solution
to this difficult problem.

### Upgrade path

In addition to the usual instructions from
https://docs.funkwhale.audio/upgrading.html, non-docker users will have
to setup an additional systemd unit file for recurrent tasks.

This was forgotten in the deployment documentation, but recurrent tasks,
managed by the celery beat process, will be needed more and more in subsequent
releases. Right now, we'll be using to clear the cache for federated music files
and keep disk usage to a minimum.

In the future, they will also be needed to refetch music metadata or federated
information periodically.

Celery beat can be enabled easily:

```sh
curl -L -o "/etc/systemd/system/funkwhale-beat.service" "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/develop/deploy/funkwhale-beat.service"
# Also edit /etc/systemd/system/funkwhale.target
# and ensure the Wants= line contains the following:
# Wants=funkwhale-server.service funkwhale-worker.service funkwhale-beat.service
nano /etc/systemd/system/funkwhale.target
# reload configuration
systemctl daemon-reload
```

Docker users already have celerybeat enabled.

## 0.8 (2018-04-02)

Features:

- Add a detail page for radios (#64)
- Implemented page title binding (#1)
- Previous Track button restart playback after 3 seconds (#146)

Enhancements:

- Added credits to Francis Gading for the logotype (#101)
- API endpoint for fetching instance activity and updated timeline to use this
  new endpoint (#141)
- Better error messages in case of missing environment variables (#140)
- Implemented a @test@yourfunkwhaledomain bot to ensure federation works
  properly. Send it "/ping" and it will answer back :)
- Queue shuffle now apply only to tracks after the current one (#97)
- Removed player from queue tab and consistently show current track in queue
  (#131)
- We now restrict some usernames from being used during signup (#139)

Bugfixes:

- Better error handling during file import (#120)
- Better handling of utf-8 filenames during file import (#138)
- Converted favicon from .ico to .png (#130)
- Upgraded to Python 3.6 to fix weird but harmless weakref error on django task
  (#121)

Documentation:

- Documented the upgrade process (#127)

### Preparing for federation

Federation of music libraries is one of the most asked feature.
While there is still a lot of work to do, this version includes
the foundation that will enable funkwhale servers to communicate
between each others, and with other federated software, such as
Mastodon.

Funkwhale will use ActivityPub as it's federation protocol.

In order to prepare for federation (see #136 and #137), new API endpoints
have been added under /federation and /.well-known/webfinger.

For these endpoints to work, you will need to update your nginx configuration,
and add the following snippets:

```nginx
location /federation/ {
    include /etc/nginx/funkwhale_proxy.conf;
    proxy_pass   http://funkwhale-api/federation/;
}
location /.well-known/webfinger {
    include /etc/nginx/funkwhale_proxy.conf;
    proxy_pass   http://funkwhale-api/.well-known/webfinger;
}
```

This will ensure federation endpoints will be reachable in the future.
You can of course skip this part if you know you will not federate your instance.

A new `FEDERATION_ENABLED` env var have also been added to control whether
federation is enabled or not on the application side. This settings defaults
to True, which should have no consequences at the moment, since actual
federation is not implemented and the only available endpoints are for
testing purposes.

Add `FEDERATION_ENABLED=false` to your .env file to disable federation
on the application side.

To test and troubleshoot federation, we've added a bot account. This bot is available at @test@yourinstancedomain,
and sending it "/ping", for example, via Mastodon, should trigger
a response.

## 0.7 (2018-03-21)

Features:

- Can now filter artists and albums with no listenable tracks (#114)
- Improve the style of the sidebar to make it easier to understand which tab is
  selected (#118)
- On artist page, albums are not sorted by release date, if any (#116)
- Playlists are here \o/ :tada: (#3, #93, #94)
- Use django-cacheops to cache common ORM requests (#117)

Bugfixes:

- Fixed broken import request admin (#115)
- Fixed forced redirection to login event with
  API_AUTHENTICATION_REQUIRED=False (#119)
- Fixed position not being reset properly when playing the same track
  multiple times in a row
- Fixed synchronized start/stop radio buttons for all custom radios (#103)
- Fixed typo and missing icon on homepage (#96)

Documentation:

- Up-to-date and complete development and contribution instructions in
  README.rst (#123)

## 0.6.1 (2018-03-06)

Features:

- Can now skip acoustid on file import with the --no-acoustid flag (#111)

Bugfixes:

- Added missing batch id in output during import (#112)
- Added some feedback on the play button (#100)
- Smarter pagination which takes a fixed size (#84)

Other:

- Completely removed django-cachalot from the codebase (#110). You can safely
  remove the CACHALOT_ENABLED setting from your .env file

## 0.6 (2018-03-04)

Features:

- Basic activity stream for listening and favorites (#23)
- Switched to django-channels and daphne for serving HTTP and websocket (#34)

### Upgrades notes

This version contains breaking changes in the way funkwhale is deployed,
please read the notes carefully.

### Instance timeline

A new "Activity" page is now available from the sidebar, where you can
browse your instance activity. At the moment, this includes other users
favorites and listening, but more activity types will be implemented in the
future.

Internally, we implemented those events by following the Activity Stream
specification, which will help us to be compatible with other networks
in the long-term.

A new settings page has been added to control the visibility of your activity.
By default, your activity will be browsable by anyone on your instance,
but you can switch to a full private mode where nothing is shared.

The setting form is available in your profile.

### Switch from gunicorn to daphne

This release include an important change in the way we serve the HTTP API.
To prepare for new realtime features and enable websocket support in Funkwhale,
we are now using django-channels and daphne to serve HTTP and websocket traffic.

This replaces gunicorn and the switch should be easy assuming you
follow the upgrade process described below.

If you are using docker, please remove the command instruction inside the
api service, as the up-to-date command is now included directly in the image
as the default entry point:

```yaml
services:
  api:
    restart: unless-stopped
    image: funkwhale/funkwhale:${FUNKWHALE_VERSION:-latest}
    command: ./compose/django/gunicorn.sh # You can remove this line
```

On non docker setups, you'll have to update the `[Service]` block of your
funkwhale-server systemd unit file to launch the application server using daphne instead of gunicorn.

The new configuration should be similar to this:

```ini
[Service]
User=funkwhale
# adapt this depending on the path of your funkwhale installation
WorkingDirectory=/srv/funkwhale/api
EnvironmentFile=/srv/funkwhale/config/.env
ExecStart=/usr/local/bin/daphne -b ${FUNKWHALE_API_IP} -p ${FUNKWHALE_API_PORT} config.asgi:application
```

Ensure you update funkwhale's dependencies as usual to install the required
packages.

On both docker and non-docker setup, you'll also have to update your nginx
configuration for websocket support. Ensure you have the following blocks
included in your virtualhost file:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    # ...
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
}
```

Remember to reload your nginx server after the edit.

## 0.5.4 (2018-02-28)

Features:

- Now stop running radio when clearing queue (#98)

Bugfixes:

- Fixed queue skipping tracks (#91)
- Now loop properly on queue when we only have one track (#95)

## 0.5.3 (2018-02-27)

Features:

- Added admin interface for radios, track files, favorites and import requests (#80)
- Added basic instance stats on /about (#82)
- Search now unaccent letters for queries like "The Dø" or "Björk" yielding more results (#81)

Bugfixes:

- Always use username in sidebar (#89)
- Click event outside of player icons (#83)
- Fixed broken import because of missing transaction
- Now always load next radio track on last queue track ended (#87)
- Now exclude tracks without file from radio candidates (#88)
- skip to next track properly on 40X errors (#86)

Other:

- Switched to towncrier for changelog management and compilation

## 0.5.2 (2018-02-26)

- Fixed broken file import due to wrong url (#73)
- More accurate mimetype detection
- Fixed really small size on small screens
- Added masonry layout for artists, requests and radios (#68)
- We now have a favicon!
- Fixed truncated play icon (#65)

## 0.5.1 (2018-02-24)

- Front: Fixed broken ajax call on radio builder (#69)
- Front: Shuffle now restart next track from beginning (#70)
- Front: volume slider should now have the same style everywhere (#72)

## 0.5 (2018-02-24)

- Front: Now reset player colors when track has no cover (#46)
- Front: play button now disabled for unplayable tracks
- API: You can now enable or disable registration on the fly, via a preference (#58)
- Front: can now signup via the web interface (#35)
- Front: Fixed broken redirection on login
- Front: Fixed broken error handling on settings and login form

About page:

There is a brand new about page on instances (/about), and instance
owner can now provide a name, a short and a long description for their instance via the admin (/api/admin/dynamic_preferences/globalpreferencemodel/).

Transcoding:

Basic transcoding is now available to/from the following formats : ogg and mp3.

_This is still an alpha feature at the moment, please report any bug._

This relies internally on FFMPEG and can put some load on your server.
It's definitely recommended you setup some caching for the transcoded files
at your webserver level. Check the the example nginx file at deploy/nginx.conf
for an implementation.

On the frontend, usage of transcoding should be transparent in the player.

Music Requests:

This release includes a new feature, music requests, which allows users
to request music they'd like to see imported.
Admins can browse those requests and mark them as completed when
an import is made.

## 0.4 (2018-02-18)

- Front: ambiant colors in player based on current track cover (#59)
- Front: simplified front dev setup thanks to webpack proxy (#59)
- Front: added some unittests for the store (#55)
- Front: fixed broken login redirection when 401
- Front: Removed autoplay on page reload
- API: Added a /instance/settings endpoint
- Front: load /instance/settings on page load
- Added settings to report JS and Python error to a Sentry instance
  This is disabled by default, but feel free to enable it if you want
  to help us by sending your error reports :) (#8)

## 0.3.5 (2018-01-07)

- Smarter BACKEND_URL in frontend

## 0.3.4 (2018-01-07)

- Fixed wrong URL construction in ajax call

## 0.3.3 (2018-01-07)

- Users can now create their own dynamic radios (#51)

## 0.3.2

- Fixed an issue in the main dockerfile

## 0.3.1

- Revamped all import logic, everything is more tested and consistent
- Can now use Acoustid in file imports to automatically grab metadata from musicbrainz
- Brand new file import wizard

## 0.2.7

- Shortcuts: can now use the `f` shortcut to toggle the currently playing track
  as a favorite (#53)
- Shortcuts: avoid collisions between shortcuts by using the exact modifier (#53)
- Player: Added looping controls and shortcuts (#52)
- Player: Added shuffling controls and shortcuts (#52)
- Favorites: can now modify the ordering of track list (#50)
- Library: can now search/reorder results on artist browsing view (#50)
- Upgraded celery to 4.1, added endpoint logic for fingerprinting audio files
- Fixed #56: invalidate tokens on password change, also added change password form
- Fixed #57: now refresh jwt token on page refresh
- removed ugly dividers in batch import list
- Fixed a few padding issues
- Now persist/restore queue/radio/player state automatically
- Removed old broken imports
- Now force tests paths
- Fixed #54: Now use pytest everywhere \o/
- Now use vuex to manage state for favorites
- Now use vuex to manage state for authentication
- Now use vuex to manage state for player/queue/radios

## 0.2.6 (2017-12-15)

- Fixed broken Dockerfile

## 0.2.5 (2017-12-15)

Features:

- Import: can now specify search template when querying import sources (#45)
- Login form: now redirect to previous page after login (#2)
- 404: a decent 404 template, at least (#48)

Bugfixes:

- Player: better handling of errors when fetching the audio file (#46)
- Csrf: default CSRF_TRUSTED_ORIGINS to ALLOWED_HOSTS to avoid Csrf issues on admin (#49)

Tech:

- Django 2 compatibility, lot of packages upgrades (#47)

## 0.2.4 (2017-12-14)

Features:

- Models: now store release group mbid on Album model (#7)
- Models: now bind import job to track files (#44)

Bugfixes:

- Library: fixen broken "play all albums" button on artist cards in Artist browsing view (#43)
