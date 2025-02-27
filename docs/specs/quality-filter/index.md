# Quality filter

## The issue

As raised in [#1469](https://dev.funkwhale.audio/funkwhale/funkwhale/-/issues/1469), the current user experience of Funkwhale can be poor if the content on a pod is of a low quality or is missing essential information. For example:

- Albums with missing metadata cause the interface appear stark and poorly maintained
- Tracks encoded at a low bitrate sound bad and give a bad impression of the software

## Proposed solution

To address this, Funkwhale should include a quality filter that enables administrators to put their pod's best quality content front and center when a user navigates to the {guilabel}`Explore` tab. This quality filter should enable the **admin** of a pod to set the following properties in the Funkwhale settings menu:

- The **format** of tracks returned by the API
- Whether to show or hide albums missing essential metadata

Metadata which might be considered essential:

- Album art
- Year of publication
- Genre tags

To give full granular control, the admin should be able to select which of these metadata are required.

## Feature behavior

### Frontend

The frontend implementation of this feature should comprise a set of controls in the Funkwhale admin menu. As noted above, this should be split up as follows in a section labeled {guilabel}`Explore page quality filter`:

- An {guilabel}`Enable` checkbox. If enabled, all options below are made available. If not enabled, no filters are applied to the API calls
- A {guilabel}`Formats` multi-select dropdown field that displays the file formats supported by Funkwhale. The admin should be able to select any combination of formats (e.g.: **MP3 + OGG + FLAC + AAC**)

Under a subsection labeled {guilabel}`Required metadata`:

- A checkbox for {guilabel}`Album art`. If checked, only albums with associated art should be returned by the API
- A checkbox for {guilabel}`Release date`. If checked, only albums with a properly formatted release date should be returned by the API
- A checkbox for {guilabel}`Genre tags`. If checked, only content that is tagged with at least one genre tag should be returned by the API
- A checkbox for {guilabel}`MusicBrainz ID`. If enabled, only content with a MusicBrainz ID is returns in API calls.

The menu should also contain a {guilabel}`Quality filter` slider that allows admins to choose a **minimum** quality level. This level should be abstracted on the backend to apply a sensible value to all supported file formats.

- {guilabel}`Off` - Allows content of **all** bitrates and formats to be displayed on the Explore page.
- {guilabel}`Low` - Allows only compressed audio formats with a lower bitrate to be displayed on the Explore page.
- {guilabel}`Medium` - Allows both low- and medium-bitrate compressed audio formats to be displayed on the Explore page.
- {guilabel}`High` - Allows uncompressed and high-bitrate compressed audio formats to be displayed on the Explore page.
- {guilabel}`Very high` - Allows only uncompressed files and very high-bitrate opus files to be displayed on the Explore page.

### Backend

Endpoints which return audio data must include a **quality** filter. This filter should enable an admin or API user to filter content by **metadata availability** and **file format** to ensure a minimum level of quality in the data returned.

The following configurable filters need to be applied:

- `format`: a comma-separated list of accepted file formats (e.g. `mp3,ogg,vorbis,flac`). Only files matching the formats in the list should be returned if this filter is passed
- `has_tags`: a boolean value that indicates whether the content should be tagged (`true`) or not (`false`)
- `has_mbid`: a boolean value that indicates whether the content has a `mbid` tag associated (`true`) or not (`false`)
- `quality`: an enum value that filters content based on the file quality. If no value is passed, uploads of any quality should be returned. Accepted values:
  - `low`
  - `medium`
  - `high`
  - `very_high`

In addition to the above, the `Albums` endpoint should contain the following filters:

- `has_cover`: a boolean value that indicates whether the album has associated album art (`true`) or not (`false`)
- `has_release_date`: a boolean value that indicates whether the album is tagged with a properly formatted release date (`true`) or not (`false`)

#### Quality filter mappings

The table below shows a suggested bitrate mapping and behavior for each file type. Bitrate values are shown in **kbps**.

|           | FLAC   | AIF    | AIFF   | Opus   | AAC    | OGG    | MP3    |
| --------- | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| Off       | always | always | always | always | always | always | always |
| Low       | never  | never  | never  | <= 96  | <= 96  | <= 96  | <= 192 |
| Medium    | never  | never  | never  | <= 128 | <= 128 | <= 192 | <= 256 |
| High      | always | always | always | <= 160 | <= 288 | <= 256 | <= 320 |
| Very high | always | always | always | >= 510 | never  | never  | never  |

## Availability

- Admin panel
- API
- CLI

## Open questions

- We need to provide sensible defaults for admins. What should these be for each setting?
- Should the quality filter be enabled by default? If so, we need to clearly communicate this to the pod admin in the interface to avoid confusion. Existing pods should have it disabled by default.

## Minimum viable product

On the backend we must:

- Create new endpoints in the `v2` namespace which can feed the "Explore" page
- Apply the required filters to the new endpoints

On the frontend we must:

- Change our API calls for the frontend to point to the new `v2` endpoints
