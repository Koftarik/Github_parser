from datetime import datetime, timedelta, date
import os
from github import Github

from config import Config

import shutil #new
import recognizer #new


class GithubClient:
    def __init__(self):
        self._client = Github(login_or_token=Config.github_access_token)

    def search_repos_by_language(self, keyword, lang, start_time=None, end_time=None):
        if start_time is None and end_time is None:
            return self._client.search_repositories(query=f'{keyword} language:{lang}')
        return self._client.search_repositories(query=f'{keyword} language:{lang} created:{start_time}..{end_time}')

    def download_files_by_ext(self, repos, ext, save_path):
        for repo in repos:
            repo_name = repo.full_name.replace('/', '__')
            if not os.path.exists(f'{save_path}/{repo_name}'):
                os.mkdir(f'{save_path}/{repo_name}')

            cashe = 'cashe'                                                 #new
            if not os.path.exists(f'{save_path}/{repo_name}/{cashe}'):      #new
                os.mkdir(f'{save_path}/{repo_name}/{cashe}')                #new

            else:
                continue
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    print(f'Processing {file_content}')
                    if file_content.name.endswith(ext):
                        with open(f'{save_path}/{repo_name}/{cashe}/{file_content.name}', 'wb') as f:     #updated
                            try:
                                f.write(file_content.decoded_content)
                            except AssertionError:
                                print(f'Unable to write {file_content.name}. No encoding specified.')

            #анализ файлов в папке cashe
            cashe_path = save_path + '\\' + repo_name + '\\' + cashe
            for filename in os.listdir(cashe_path):
                if recognizer.recognize(filename):
                    os.replace (cashe_path + '\\' + filename, save_path + '\\' + repo_name + '\\' + filename)
            #os.rmdir(cashe_path) #удаление папки cashe
                    

    def get_rate_limit_refresh_time(self, time_hours_delta=3):
        return datetime.combine(date.today(), self._client.get_rate_limit().core.reset.time()) + timedelta(hours=time_hours_delta)
