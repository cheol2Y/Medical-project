from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import os
from scrape_utils import append_to_csv 
from datetime import datetime
from dotenv import load_dotenv
import json

def fetch(url):
    with requests.get(url) as response:
        response.raise_for_status()
        return response.text

def scrape_details(doc_id):
    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')
    base_url = "https://kin.naver.com/qna/detail.naver?d1id=7&dirId=70201&docId={}"
    # headers = {
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    #     "Cache-Control": "max-age=0",
    #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    #     "Upgrade-Insecure-Requests": "1",
    # }
    url = base_url.format(doc_id)

    # CPU 코어 수를 기반으로 max_workers 계산
    cpu_cores = os.cpu_count()
    if cpu_cores:
        max_workers = cpu_cores * 2  # I/O 바운드 작업 가정, 코어 수의 2배 사용
    else:
        max_workers = 4  # CPU 코어 수를 결정할 수 없는 경우 기본값 사용

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future = executor.submit(fetch, url)    # header는 생략했음
        html = future.result()
        soup = BeautifulSoup(html, "html.parser")
        
        data = {
            'doc_id': doc_id,
            'title': soup.select_one('.title').text.strip() if soup.select_one('.title') else 'N/A',
            'question': soup.select_one('.c-heading__content').text.strip() if soup.select_one('.c-heading__content') else (soup.select_one('.c-heading__title').text.strip() if soup.select_one('.c-heading__title') else 'N/A'),
            'answer': soup.select_one('.se-main-container').text.strip() if soup.select_one('.se-main-container') else (soup.select_one('._endContentsText.c-heading-answer__content-user').text.strip() if soup.select_one('._endContentsText.c-heading-answer__content-user') else 'N/A'),
        }

        # CSV 파일에 데이터 저장하는 로직
        csv_file_name = f"details_{today_str}_QNA.csv"
        csv_file_path = os.path.join("./csv_folder/today_naver_QnA", csv_file_name)
        append_to_csv(data, csv_file_path)
        # webhook_url = os.getenv("SLACK_WEBHOOK_URL_MEDICAL")
        # if webhook_url:
        #     message = {"text": "네이버 QnA 수집 완료 !"}
        #     response = requests.post(
        #         webhook_url,
        #         data=json.dumps(message),
        #         headers={"Content-Type": "application/json"},
        #     )
        #     print(response.status_code, response.text)
        # else:
        #     print("SLACK_WEBHOOK_URL_MEDICAL 환경 변수가 설정되지 않았습니다.")

