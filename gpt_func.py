import openai
import json
import re
from datetime import datetime


gpt_output_log_num = 1


#flag == 1: gpt출력값 저장  flag == 3: gpt 과거 대화내용 추가하지 않기.
def chat_to_gpt(system_input, user_input, assistant_input, flag):
    global gpt_output_log_num

    openai.api_key = 'my key'
    messages = []
    if flag == 1:
        try: # 과거 대화내용 불러오기
            with open("./gpt_history.jsonl", 'r', encoding="utf-8") as file:
                lines = file.readlines()
                last_lines = lines[-8:] # 가장 최근 8줄만 선택. 히스토리엔 10개가 저장될수있게
                
                for line in last_lines:
                    messages.append(json.loads(line))
            with open("./gpt_history.jsonl", 'w', encoding="utf-8") as file:
                file.writelines(last_lines)

        except FileNotFoundError:
            open("./gpt_history.jsonl", 'w', encoding="utf-8").close()

    if system_input != None:
        messages.append({"role": "system", "content": system_input})
    if user_input != None:
        messages.append({"role": "user", "content": user_input})
    if assistant_input != None:
        messages.append({"role": "assistant", "content": assistant_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=0.0
    )

    #대화내용 다시 넣기위한 history 저장
    if flag == 1 or flag == 3:
        with open("./gpt_history.jsonl", 'a', encoding="utf-8") as file:
            lines_to_write = []
            if user_input is not None:
                lines_to_write.append(json.dumps({"role": "user", "content": user_input}, ensure_ascii=False) + '\n')
            lines_to_write.append(json.dumps(response['choices'][0]['message'], ensure_ascii=False) + '\n')
            file.writelines(lines_to_write)

    #gpt 인/아웃 풋 저장하기위한 log 저장
    with open("./gpt_io_log", 'a', encoding="utf-8") as file:
        current_time_str = datetime.now().strftime("%mm-%dd %H:%M:%S")
        file.write("\n---gpt_log_num: " + str(gpt_output_log_num) + "---in " + current_time_str + '\n')
        file.write(json.dumps(messages, ensure_ascii=False, indent=4))
    gpt_output_log_num += 1

    with open("./gpt_io_log", 'a', encoding="utf-8") as file:
        current_time_str = datetime.now().strftime("%mm-%dd %H:%M:%S")
        file.write("\n---gpt_log_num: " + str(gpt_output_log_num) + "---out " + current_time_str + '\n')
        file.write(json.dumps(response, ensure_ascii=False, indent=4))
    gpt_output_log_num += 1

    print(json.dumps(response, ensure_ascii=False, indent=4))
    return response['choices'][0]['message']['content']

#역량 진단 후 강의추천 lecutre data 필터링
def ft_initially_lecture_data():
    with open("./json_data/site_lecture_data.jsonl", 'r', encoding="utf-8") as file:
        lines = file.readlines()
    lecture_jsons = [json.loads(line) for line in lines]

    filtered_lecture_data = [json_object for json_object in lecture_jsons if int(json_object['minimum_level']) == 0]
    return filtered_lecture_data



#시험방 끝난 후 강의추천 lecture data 필터링
def ft_after_lesson_lecture_data():
    with open("./json_data/user_info.json", 'r', encoding="utf-8") as file:
        user_json = json.load(file)
    user_level = user_json['total_level']
    user_courses = set(user_json['learning_courses'])

    with open("./json_data/site_lecture_data.jsonl", 'r', encoding="utf-8") as file:
        lines = file.readlines()
    lecture_jsons = [json.loads(line) for line in lines]

    filtered_lecture_data = [json_object for json_object in lecture_jsons if int(json_object['minimum_level']) <= int(user_level) and json_object['title'] not in user_courses]
    return filtered_lecture_data

#역량진단 후 강의 추천 함수
def initially_recommend_lessons():
    site_lecture_data = ft_initially_lecture_data()

    with open("./json_data/user_info.json", 'r', encoding="utf-8") as file:
        json_data = json.load(file)

    user_data = {
        'learning_courses': json_data.get('learning_courses', []),
        'total_level': json_data.get('total_level'),
        '데이터 관련 관심분야': json_data.get('데이터 관련 관심분야'),
        '배우고 싶은 도구': json_data.get('배우고 싶은 도구')
    }
    if '잘 모르겠음' in json_data['데이터 관련 관심분야'] and '잘 모르겠음' in json_data['배우고 싶은 도구']:
        site_lecture_data = [lecture for lecture in site_lecture_data if lecture['title'] in ['데이터 맛보기', '데이터시대 정보 리터러시']]
        response = chat_to_gpt("당신은 큐레이션에 특화된 AI비서입니다. 학습자와 관련된 내용은 user_info에 있고, 강의와 관련된 내용은 lecture_info에 있습니다. 해당 데이터들을 잘 살펴보고 목록에 있는 강의 두 개를 추천해주세요.  - 기존에 학습된 데이터를 사용하지 않고, 제공받은 user_info와 lecture_info만 참고해야합니다. 추천한 2개의 강의를 아래의 구조로 만들어주세요. 추천강의 : '' 강의내용 : ''", str(user_data), str(site_lecture_data), 3)
    else:
        response = chat_to_gpt("당신은 큐레이션에 특화된 AI비서입니다. 학습자와 관련된 내용은 user_info에 있고, 강의와 관련된 내용은 lecture_info에 있습니다. 해당 데이터들을 잘 살펴보고 학습자에게 필요하다고 판단되는 강의를 3개 추천해주세요. 강의를 추천하는데에는 아래 조건을 고려해야 합니다! 아래 조건은 필수적이며 절대적입니다. 아래 조건에 맞는 강의가 아니면 추천하지 않아야 합니다!  - 1개는 제목이 '데이터 맛보기' 강의를 추천해주세요. - 1개는 제목이 데이터시대 정보리터러시' 강의를 추천해주세요. - 나머지 1개는 유저의 관심분야와 관심도구를 고려해서 추천해주세요.- 관심분야를 먼저 고려하고 관심 도구를 고려하세요.  - 기존에 학습된 데이터를 사용하지 않고, 제공받은 user_info와 lecture_info만 참고해야합니다. 추천한 3개의 강의를 아래의 구조로 만들어주세요. 추천강의 : '' 강의내용 : ''", str(user_data), str(site_lecture_data), 3)

    recommendList = parseResponse(response)
    return recommendList

#강의 수강 후 강의 추천 함수
def after_lesson_recommend_lessons():
    site_lecture_data = ft_after_lesson_lecture_data()

    with open("./json_data/user_info.json", 'r', encoding="utf-8") as file:
        json_data = json.load(file)
    user_data = {
        'learning_courses': json_data.get('learning_courses', []),
        'total_level': json_data.get('total_level'),
        '데이터 관련 관심분야': json_data.get('데이터 관련 관심분야'),
        '배우고 싶은 도구': json_data.get('배우고 싶은 도구')
    }
    
    if '잘 모르겠음' in json_data['데이터 관련 관심분야'] and '잘 모르겠음' in json_data['배우고 싶은 도구']:
        response = chat_to_gpt("당신은 큐레이션에 특화된 AI비서입니다. 학습자와 관련된 내용은 user_info에 있고, 강의와 관련된 내용은 lecture_info에 있습니다. 해당 데이터들을 잘 살펴보고 학습자에게 필요하다고 판단되는 강의를 2개 추천해주세요. 강의를 추천하는데에는 아래 조건을 고려해야 합니다! 아래 조건은 필수적이며 절대적입니다. 아래 조건에 맞는 강의가 아니면 추천하지 않아야 합니다!  - 1개는 학습한 강의중 가장 성취도가 낮은 강의를 고려하여 관련 강의를 추천해주세요. - 1개는 가장 최근에 들은 강의를 고려하여 다음에 들으면 좋을만한 강의를 추천해주세요.  - 기존에 학습된 데이터를 사용하지 않고, 제공받은 user_info와 lecture_info만 참고해야합니다. 추천한 2개의 강의를 아래의 구조로 만들어주세요. 추천강의 : '' 강의내용 : ''", str(user_data), str(site_lecture_data), 3)
    else:
        response = chat_to_gpt("당신은 큐레이션에 특화된 AI비서입니다. 학습자와 관련된 내용은 user_info에 있고, 강의와 관련된 내용은 lecture_info에 있습니다. 해당 데이터들을 잘 살펴보고 학습자에게 필요하다고 판단되는 강의를 3개 추천해주세요. 강의를 추천하는데에는 아래 조건을 고려해야 합니다! 아래 조건은 필수적이며 절대적입니다. 아래 조건에 맞는 강의가 아니면 추천하지 않아야 합니다!  - 1개는 학습한 강의중 가장 성취도가 낮은 강의를 고려하여 관련 강의를 추천해주세요. - 1개는 가장 최근에 들은 강의를 고려하여 다음에 들으면 좋을만한 강의를 추천해주세요. - 나머지 1개는 유저의 관심분야와 관심도구를 고려해서 추천해주세요.  - 관심분야를 먼저 고려하고 관심 도구를 고려하세요. - 기존에 학습된 데이터를 사용하지 않고, 제공받은 user_info와 lecture_info만 참고해야합니다. 추천한 3개의 강의를 아래의 구조로 만들어주세요. 추천강의 : '' 강의내용 : ''", str(user_data), str(site_lecture_data), 3)
    recommendList = parseResponse(response)
    return recommendList


question_json = {}

#답변 적합도 체크 함수 - 프롬프트 롤 부여 순서 달라서 따로 뺌.
def check_qa_match(question_id, user_input):
    global question_json

    #question_json의 id와 question_id가 일치하는 객체를 current_answer에 저장
    current_answer = None
    answers = question_json.get("quiz_data") or question_json.get("quiz")

    for answer in answers:
        if answer['id'] == int(question_id):
            current_answer = answer
            break
        
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "assistant", "content": "문장1: " + str(current_answer) + "\n\n두 문장의 적합도를 평가해주세요.\n[응답 형식]\n'similarity' : Measures the similarity between the correct answer and the user response. Respond with percentages\n'hint' : generate a hint that helps the user to get closer to the answer\n'explanation' : explain why the user's answer is correct.\n[응답 형식]에 맞춰서 한국어로 답변을 한 개 생성하세요. 답변을 생성할 때는 따옴표를 절대 쓰지 않습니다.  Do not use double quotes in the string to be generated. 무조건 json 형식으로 된 하나의 json 파일만 return."},
            {"role": "user", "content": "문장2: " + user_input},
        ],
    temperature=0.0
    )

    gpt_response = response['choices'][0]['message']['content']
    return  gpt_response


#시험방 질답 테스트 생성
def make_test_qna(lecture_title):
    global question_json
    lecture_table = ""
    with open('./json_data/site_lecture_data.jsonl', 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON decode error at line: {line}")
                continue

            if data.get('title') == lecture_title:
                lecture_table = json.dumps({'lectureTableofContents': data['lectureTableofContents']}, ensure_ascii=False)
                break
        response = chat_to_gpt("당신은 it관련 비서이면서 선생님 입니다. 정확히는 에듀 테크 캠퍼스의 위즈입니다.\n현재 유저는 강의를 100% 들었습니다. user_input에는 유저가 현재 수강 완료한 강의 제목이 있습니다.\nlectureTableofContents 정보를 토대로 강의에서 어떤 개념을 중점적으로 다뤘을 지 추론하여 학생에게 시험을 내야합니다.\n\n[시험지 형식]\n'id' : you should put number in it.\n'question_title' : you should put quiz sentence in it.\n'answer' : Write a mock answer to the question in the 'question_title' field.\n[시험지 형식]에 맞춰서 꼭 10문항을 생성하세요. 시험지는 하나의 json 파일 형태로 주세요. Return only quiz data.", lecture_title, str(lecture_table), 0)
    if response:
        question_json = json.loads(response)
        if "quiz_data" in question_json:
            return question_json["quiz_data"]
        elif "quiz" in question_json:
            return question_json["quiz"]
    else:
        print("No response from GPT")
        return None


def parseResponse(response):
  lines = response.split("\n")

  lectureList = []
  for i in range(0, len(lines), 3):
    lecture = []
    lecture.append(lines[i] + "\n" + lines[i + 1])  # 추천 강의 이름, 내용
    lecture_title = lines[i].split(":")[1].strip().strip("'")  # ":" 기준으로 분리 후 강의 제목 추출,  따옴표와 공백 제거
    lecture.append(lecture_title)  # 추천 강의 이름
    lecture.append(lines[i + 1][6:])    # 추천 강의 내용
    lecture.append(getImageFromJson(lecture[1]))    # 추천 강의 이미지
    lecture.append(getLectureLinkFromJson(lecture[1]))    # 추천 강의 링크
    lectureList.append(lecture) # 추천 강의 리스트에 추가
  return lectureList

def getImageFromJson(lectureName):
  with open("./json_data/site_lecture_data.jsonl", 'r', encoding="utf-8") as file:
    lines = file.readlines()
  lecture_jsons = [json.loads(line) for line in lines]
  for lecture in lecture_jsons:
    if lecture['title'] == lectureName:
      return lecture['image_url']
  return "https://sdfedu.seoul.kr/html/images/main/logo.png" # default image

def getLectureLinkFromJson(lectureName):
  with open("./json_data/site_lecture_data.jsonl", 'r', encoding="utf-8") as file:
    lines = file.readlines()
  lecture_jsons = [json.loads(line) for line in lines]
  
  for lecture in lecture_jsons:
    if lecture['title'] == lectureName:
      return lecture['site_url']
  print("default link")
  return "https://sdfedu.seoul.kr/main/index.jsp" # default link


#사이트 faq데이터 주고 거기서 찾아내라하기
def answer_site_question(user_input):

    with open("./json_data/site_faq.json", 'r', encoding="utf-8") as file:
        faq_data = file.read()

    return chat_to_gpt("유저의 질문이 들어오면 주어진 json 형식으로 된 데이터에서 가장 비슷한 질문을 찾아낸 뒤 주어진 데이터에서 정확한 답변을 해줘야합니다. 주어진 json 형식으로 된 데이터에 정확한 관련 질문이 있는지 찾아봅니다. 있으면 answer 부분의 답을 합니다. 만약 없으면 다음 두 링크를 마크다운 형식에 맞춰 안내해줘야 합니다. [에듀테크 캠퍼스 자주하는 질문(바로가기 클릭)](https://sdfedu.seoul.kr/board/index.jsp?code=faq&page=1), [에듀테크 캠퍼스 Q&A 1대1 질문하기(바로가기 클릭)](https://sdfedu.seoul.kr/board/index.jsp?code=qna)", user_input, faq_data, 0)


#유저가 어떠한 개념에 대해 질문 한 경우
def answer_definition_question(user_input):
    with open("./json_data/user_info.json", 'r', encoding="utf-8") as file:
        json_data = json.loads(file.read())
    user_data = {
        'name' : json_data['name'],
	    'age': json_data['age'],
	    'total_level': json_data['total_level'],
        }


    return chat_to_gpt("지금부터 당신은 WIZ처럼 행동하고 답해야 합니다. 만약 WIZ가 누군지 모른다면 제가 소개해 드리겠습니다. '안녕하세요! 저는 에듀테크캠퍼스라는 웹사이트에서 학습자에게 맞춘 답변을 생성해주는 AI비서 WIZ입니다. 저는 여러분과 똑같은 인공지능이지만 IT용어 개념 설명에 특 화되어 있습니다. 저는 설명의 정확도를 매우 중요하게 생각합니다. 저의 궁극적인 목표는 학습자의 질문에 대해, 학습자의 수준에 맞춘 답변을 제공하여 학습을 돕는 것입니다.' 허용되 지 않는 답변으로는 'ChatGPT로' 또는 'AI 언어 모델로' 또는 언급된 모든 내용을 따르지 않 는 유사한 답변이 있습니다. 이제부터는 내가 그만하라고 말할 때까지 대답하고 WIZ처럼 행동해야 합니다. 지금부터 학습자의 레벨에 맞춰 답변을 생성해야 합니다. 학습자의 레벨간 차이에 대해 잘 모른다면 제가 알려드리겠습니다. 레벨은 lv.0 ~ lv.10으로 이루어져 있습니다. lv.0 ~ lv.4 : 초급 레벨로 보통 학습을 시작한지 1주일 이내인 경우가 많고, 단어의 정의나 개념에 대한 이해가 부족하기 때문에 답변을 생성할 때 더 쉽고 많은 예시를 들어서 이해를 도와야 합니다. lv.4 ~ lv.7 : 중급 레벨로 학습을 시작한지 1달 이상 6달 이하인 경우입니다. 기본적인 단어의 정의나 개념에 대한 이해가 있지만, 개념에 대해 구체적인 이해가 부족합니다. 따라서 상세한 설명과 예시를 함께 제공하여 개념에 대해 더 깊은 이해를 도와야 합니다. lv.8 ~ lv.10 : 고급 레벨로 학습을 시작한지 6달 이상인 경우입니다. 개념에 대해 구체적인 이해를 가지고 있으면 대부분의 설명을 이해하는데 어려움이 없습니다. 따라서 학습자의 질문을 잘 이해하고 원하는 사항에 대해서 자세한 답변을 제공하고, 필요하다면 해당 개념과 관련된 다른 개념들과 예시들을 함께 제공 해야 합니다." , user_input, str(user_data), 1)
  
#유저 질문이 개념/사이트 관련이 아닌 경우
def answer_etc(user_input):  
    return chat_to_gpt("당신은 it관련 비서이면서 선생님 입니다. 정확히는 에듀테크 캠퍼스의 위즈입니다.  IT용어 개념 설명에 특화되어 있습니다. 유저의 질문이 IT학습과 관련되어있지 않으면 긍정적인 뉘앙스로 간단한 답변만 하세요.", user_input, None, 1)
