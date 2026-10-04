import sqlite3
import json
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. 환경 설정
# ---------------------------------------------------------
GEMINI_API_KEY = "AQ.Ab8RN6I5Dyu7xsK2YNacfRkKzFD7a4sYywQ6uI0UjAhsglhoNQ" # 본인의 API 키로 변경하세요
client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# 2. 로컬 DB 생성 (창고 짓기)
# ---------------------------------------------------------
def setup_database():
    # 작업 폴더에 'local_news.db' 파일이 없으면 새로 만들고, 있으면 연결합니다.
    conn = sqlite3.connect('local_news.db')
    cursor = conn.cursor()

    # 언론사 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS media_outlets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        baseline_perspective TEXT NOT NULL
    )''')

    # 기사 원문 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        media_id INTEGER,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY(media_id) REFERENCES media_outlets(id)
    )''')

    # 분석 결과 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS article_analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id INTEGER,
        predicted_perspective TEXT NOT NULL,
        confidence_score REAL,
        core_values TEXT,
        problem_diagnosis TEXT,
        detected_keywords TEXT,
        cited_sources TEXT,
        proposed_solution TEXT,
        opposite_perspective_name TEXT,
        perspective_contrast_summary TEXT,
        FOREIGN KEY(article_id) REFERENCES articles(id)
    )''')

    # 기본 언론사 데이터 1개 임시 추가 (최초 1회만)
    cursor.execute("INSERT OR IGNORE INTO media_outlets (name, baseline_perspective) VALUES ('한겨레', '진보')")

    conn.commit()
    return conn

# ---------------------------------------------------------
# 3. Gemini AI 성향 분석
# ---------------------------------------------------------
def analyze_article_bias(title: str, content: str, media_name: str) -> dict:
    system_instruction = """
    당신은 뉴스 성향 분석 AI입니다.
    응답은 반드시 아래 JSON 구조로만 출력하세요.
    {"predicted_perspective": "보수/진보/중도", "confidence_score": 0.9, "core_values": ["가치1"], "problem_diagnosis": "요약", "detected_keywords": ["단어"], "cited_sources": ["인물"], "proposed_solution": "요약", "opposite_perspective_name": "반대관점", "perspective_contrast_summary": "반대요약"}
    """
    prompt = f"언론사: {media_name}\n제목: {title}\n본문:\n{content}"

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    return json.loads(response.text)

# ---------------------------------------------------------
# 4. 실행 및 DB 저장 (물건 쌓기)
# ---------------------------------------------------------
if __name__ == "__main__":
    test_media = "한겨레"
    test_title = "노동계, 최저임금 인상 촉구"
    test_content = "양대 노총은 서민 생존권을 위해 최저임금 인상이 시급하다고 강조했다."

    # 1. DB 준비
    conn = setup_database()
    cursor = conn.cursor()

    # 2. AI 분석
    print("🤖 AI 분석 중...")
    analysis = analyze_article_bias(test_title, test_content, test_media)
    print("완료!")

    # 3. DB 저장
    # 3-1) 기사 저장
    cursor.execute("SELECT id FROM media_outlets WHERE name = ?", (test_media,))
    media_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO articles (media_id, title, content) VALUES (?, ?, ?)", (media_id, test_title, test_content))
    article_id = cursor.lastrowid

    # 3-2) 분석 결과 저장
    cursor.execute("""
        INSERT INTO article_analysis_results (
            article_id, predicted_perspective, confidence_score, core_values,
            problem_diagnosis, detected_keywords, cited_sources, proposed_solution,
            opposite_perspective_name, perspective_contrast_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article_id, analysis["predicted_perspective"], analysis["confidence_score"],
        json.dumps(analysis["core_values"], ensure_ascii=False), analysis["problem_diagnosis"],
        json.dumps(analysis["detected_keywords"], ensure_ascii=False), json.dumps(analysis["cited_sources"], ensure_ascii=False),
        analysis["proposed_solution"], analysis["opposite_perspective_name"], analysis["perspective_contrast_summary"]
    ))

    conn.commit()
    conn.close()
    print(f"✅ 모든 데이터가 local_news.db에 저장되었습니다! (Article ID: {article_id})")