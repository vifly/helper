import argparse
import json
import os
import subprocess
import requests
import tqdm
from requests.compat import urljoin, urlparse

from conf import *


def get_commander_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force_download",
        action="store_true",
        help="Use it to force download releases when file is exist")
    parser.add_argument(
        "--no_update_repo",
        action="store_true",
        help=
        "Just download releases, don't use repo-add to update Arch local repository"
    )
    args = parser.parse_args()
    return args


def strip_scheme(url: str) -> str:
    parse_result = urlparse(url)
    scheme = f"{parse_result.scheme}://"
    return parse_result.geturl().replace(scheme, '', 1)


def get_github_repos_latest_releases_api_url(user_name: str,
                                             repo_name: str) -> str:
    api_url = f"https://api.github.com/repos/{user_name}/{repo_name}/releases/latest"
    api_url = strip_scheme(api_url)
    return urljoin(ProxyURL, api_url)


def get_github_latest_releases_download_url(user_name: str,
                                            repo_name: str) -> list:
    """Get all latest releases download URLs via GitHub API.
    
    Args:
        user_name (str): GitHub username
        repo_name (str): GitHub repository name
    
    Returns:
        list: releases download URLs
    """
    api_url = get_github_repos_latest_releases_api_url(user_name, repo_name)
    api_response = requests.get(api_url)
    if api_response.status_code != 200:
        print(
            f"Can not get {api_url}, status code: {api_response.status_code}")
        print(api_response.text)
        return

    api_response_json = json.loads(api_response.text)
    download_urls = [
        i["browser_download_url"] for i in api_response_json["assets"]
    ]
    proxy_download_urls = [
        urljoin(ProxyURL, strip_scheme(url)) for url in download_urls
    ]

    return proxy_download_urls


def download_file(url: str, storage_path: str, force_download: bool = False):
    """Download file at the given URL, can download large file.
    
    Args:
        url (str): File's URL
        storage_path (str): Download file storage path
        force_download (bool, optional): True if the file is exist and you want 
        to overwrite it. Defaults to False.
    """
    if os.path.exists(storage_path) and not force_download:
        print(f"{storage_path} is exist, pass.")
        return
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        file_length = int(r.headers.get("content-length"))
        pbar = tqdm.tqdm(total=file_length, unit='B', unit_scale=True)
        with open(storage_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    pbar.update(8192)
                else:
                    pbar.close()


def update_arch_repo(package_path: str, repo_path: str, repo_name: str):
    db_path = os.path.join(repo_path, repo_name + ".db.tar.gz")
    subprocess.run(
        f"repo-add {db_path} {os.path.join(package_path, '*.tar.xz')}",
        shell=True)


def main():
    args = get_commander_args()
    abs_download_path = os.path.abspath(os.path.expanduser(DownloadPath))
    abs_repo_path = os.path.abspath(os.path.expanduser(ArchRepoDBPath))
    download_urls = get_github_latest_releases_download_url(
        UserName, GitHubRepoName)
        
    for url in download_urls:
        file_name = urlparse(url).path.split('/')[-1]
        print(f"Downloading {file_name} to {abs_download_path}.")
        download_file(url, os.path.join(abs_download_path, file_name),
                      args.force_download)

    if not args.no_update_repo:
        print(f"Update Arch local repository {ArchRepoName} in {abs_repo_path}.")
        update_arch_repo(abs_download_path, abs_repo_path, ArchRepoName)


if __name__ == "__main__":
    main()
