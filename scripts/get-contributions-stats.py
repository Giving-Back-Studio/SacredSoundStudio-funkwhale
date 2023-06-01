#!/usr/bin/env python3

import argparse
import os

import requests

GITLAB_URL = "https://dev.funkwhale.audio"
GITLAB_PROJECT_ID = 17
WEBLATE_URL = "https://translate.funkwhale.audio"
WEBLATE_COMPONENT_ID = "funkwhale/front"


def get_issues(next_release):
    url = GITLAB_URL + "/api/v4/issues"
    while url:
        response = requests.get(
            url,
            params={"per_page": 20, "milestone": next_release, "scope": "all"},
            headers={"PRIVATE-TOKEN": os.environ["PRIVATE_TOKEN"]},
        )
        response.raise_for_status()
        yield from response.json()

        if "next" in response.links:
            url = response.links["next"]["url"]
        else:
            url = None


def get_merge_requests(next_release):
    url = GITLAB_URL + "/api/v4/merge_requests"
    while url:
        response = requests.get(
            url,
            params={"per_page": 20, "milestone": next_release, "scope": "all"},
            headers={"PRIVATE-TOKEN": os.environ["PRIVATE_TOKEN"]},
        )
        response.raise_for_status()
        yield from response.json()

        if "next" in response.links:
            url = response.links["next"]["url"]
        else:
            url = None


def get_participants(project_id, issue_iid, object_type="issues"):
    if object_type not in ["issues", "merge_requests"]:
        raise ValueError("object_type needs to be `issues` or `merge_requests`")
    url = GITLAB_URL + "/api/v4/projects/{}/{}/{}/participants".format(
        project_id, object_type, issue_iid
    )

    response = requests.get(
        url,
        params={"per_page": 100},
        headers={"PRIVATE-TOKEN": os.environ["PRIVATE_TOKEN"]},
    )
    response.raise_for_status()

    participants = []
    for participant in response.json():
        participants.append(participant["name"])

    return participants


def clear_list(inList):
    outList = list(dict.fromkeys(inList))
    try:
        outList.remove("funkwhale-bot")
    except (IndexError, ValueError):
        pass
    try:
        outList.remove("weblate (bot)")
    except (IndexError, ValueError):
        pass
    outList.sort()
    return outList


def main():
    if "PRIVATE_TOKEN" not in os.environ:
        print("Please configure an Gitlab Access token in $PRIVATE_TOKEN")
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("next_tag")
    args = parser.parse_args()
    issues = get_issues(args.next_tag)
    mrs = get_merge_requests(args.next_tag)

    print("\nContributors to our Issues:\n")
    issue_participants = []

    for issue in issues:
        participants = get_participants(issue["project_id"], issue["iid"])
        issue_participants.extend(participants)

    issue_participants = clear_list(issue_participants)
    for contributor in issue_participants:
        print("- " + contributor)

    print("\nContributors to our Merge Requests:\n")
    mr_participants = []

    for mr in mrs:
        participants = get_participants(mr["project_id"], mr["iid"], "merge_requests")
        mr_participants.extend(participants)

    mr_participants = clear_list(mr_participants)
    for contributor in mr_participants:
        print("- " + contributor)

    return


if __name__ == "__main__":
    main()
