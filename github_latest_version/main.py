import argparse

from queue import Queue
from github.GithubException import RateLimitExceededException

from github_api.github_client import GithubClient
from github_api.utils import chunkify_search_results
from github_api.worker.thread_worker import DownloadFilesWorker
from utils import get_date_intervals
from db.repositories.created_intervals import CreatedIntervalsRepository
from db.session import session
from db.init_db import init_db


def main(cmd_args):
    github_client = GithubClient()

    start_date = cmd_args.start_date
    end_date = cmd_args.end_date
    intervals = get_date_intervals(start_date=start_date, end_date=end_date)

    init_db()

    db_repo = CreatedIntervalsRepository(session)
    db_repo.fill_db_with_intervals(intervals)

    for item in db_repo.get_incomplete_intervals():
        try:
            print(f'Starting {item.start_date} - {item.end_date}')
            search_results = github_client.search_repos_by_language(keyword='verilog', lang='verilog', start_time=item.start_date, end_time=item.end_date)
            print(f'Total count = {search_results.totalCount}')
            chunk_results = chunkify_search_results(search_results)

            queue = Queue()

            for _ in range(10):
                worker = DownloadFilesWorker(queue, github_client)
                worker.daemon = True
                worker.start()

            for chunk in chunk_results:
                queue.put((chunk, '.v', 'verilog_files'))
            queue.join()
            print(f'Finished {item.start_date} - {item.end_date}')
            db_repo.set_status_to_finished(start_date=str(item.start_date), end_date=str(item.end_date))
        except RateLimitExceededException:
            print(f'Rate limit exceeded! Next possible time to run script is {github_client.get_rate_limit_refresh_time()}')
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=str, help='Start date for intervals')
    parser.add_argument('--end-date', type=str, help='End date for intervals')
    args = parser.parse_args()
    main(args)
