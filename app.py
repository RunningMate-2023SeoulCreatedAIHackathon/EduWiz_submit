# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import markdown
import re
from gpt_func import *


app = Flask(__name__)
CORS(app)

# @app.route 종류
# 1. /get_question
# 2. /check_answer
# 3. /gpt-response
# 4. /sign-in
# 5. /update-user-info
# 6. /gpt-recommend

#  ----------------시험방 통신 서버----------------
# 문제


question_data = {}
# 서버에서 익스텐션으로 질문지를 보냄
@app.route('/get_question', methods=['GET'])
def get_question():
    global question_data
    lecture = re.sub(r'\[.*?\]\s*', '', request.args.get('lecture_name'))
    question_data = make_test_qna(lecture)
    if not question_data:  # 만약 question_data가 None이라면 오류 메시지를 반환합니다.
        return jsonify({'error': 'No question data found for the given lecture name'})

    questions = []
    for question in question_data:
        questions.append({
            'id': question['id'],
            'question_title': question['question_title']
        })

    return jsonify(questions)


# 익스텐션에서 서버로 사용자의 답변을 받고, 정확도와 피드백을 전송함
@app.route('/check_answer', methods=['POST'])
def check_answer():
    global question_data
    data = request.json
    user_answer = data['answer']
    question_id = data['question_id']

    for question in question_data:
        if question['id'] == int(question_id):
            question_title = question['question_title']
            correct_answer = question['answer']

            # check_qa_match 함수 호출
            gpt_response = check_qa_match(question_id, user_answer)

            print("GPT Response: ", gpt_response)  # gpt_response 내용 출력

            # JSON 문자열로 인식되지 않으면 에러를 반환하도록 함
            try:
                gpt_response_dict = json.loads(gpt_response)
            except json.JSONDecodeError:
                return jsonify({'error': 'GPT response is not JSON formatted'})

            # similarity와 feedback 값을 설정
            similarity = int(gpt_response_dict['similarity'])
            if similarity >= 80:
                feedback = gpt_response_dict['explanation']
            else:
                feedback = gpt_response_dict['hint']
            print(similarity, feedback)
            return jsonify({'similarity': similarity, 'feedback':feedback})
    
    return jsonify({'error': 'Question not found'})

#  ----------------시험방 통신 서버----------------


#gpt_response 답변을 /gpt-response로 보내는 함수 작성
@app.route('/gpt-response', methods=['POST'])
def gpt_response():
    if request.method == 'POST':
        # POST 메서드로 들어온 요청에 대한 처리 로직 작성
        data = request.get_json()
        user_input = data.get('data')

        # user_input이 없는 경우 확인
        if user_input == None:
            print(data)
            return 'Bad Request', 400

    question_type = chat_to_gpt("지금 프롬프트는 너의 아웃풋을 활용해서 분기를 나눌거야. 반드시 지금 답변은 '사이트질문, IT질문, 그외'외의 다른 말은 절대 할 수 없어. 유저의 입력을 받으면 사이트 질문인지, IT개념에 대한 질문인지, 다른 질문인지 생각해보고 절대적으로 사이트질문, 개념질문, 그외 중 한 단어로만 답변해야 해. 아래는 각 질문에 대한 설명이야. 사이트질문 : 홈페이지내에서 일어날 수 있는 오류와 관련된 문의사항. IT질문 : 프로그래밍 및 빅데이터와 관련된 질문. 그외 : 강의 추천 관련, 위즈에 대한 질문 이거나 사이트질문, 개념질문이 아닌 경우.", user_input, None, 0)
    if question_type == "사이트질문":
        response = answer_site_question(user_input)
    elif question_type == "IT질문":
        response = answer_definition_question(user_input)
    else :
        response = answer_etc(user_input)
    
    html = markdown.markdown(response)
    return {"gpt_response": html} # 적절한 GPT 답변을 응답합니다.


#userInfo_response 답변을 /userInfo로 보내는 함수 작성
@app.route('/sign-in', methods=['POST'])
def login():
    if request.method == 'POST':
        # POST 메서드로 들어온 요청에 대한 처리 로직 작성
        data = request.get_json()
        username = data.get('id')
        password = data.get('pw')

    # 여기서 username과 password를 처리하는 로직을 작성합니다.
    # 이 예제에서는 username이 'admin'이고 password가 'password'인 경우에만 로그인 성공으로 처리합니다.
    if username == 'admin' and password == 'password':
        with open("./json_data/user_info.json", 'r', encoding="utf-8") as file:
            user_info = file.read()  # 사용자 정보
            print(user_info)
        return {'status': 'success', 'message': '로그인 성공', 'user_info': user_info}
    else:
        return {'status': 'failure', 'message': '로그인 실패'}

#updateUserInfo 답변을 /update-user-info로 보내는 함수 작성
@app.route('/update-user-info', methods=['POST'])
def update_user_info():
    if request.method == 'POST':
        # POST 메서드로 들어온 요청에 대한 처리 로직 작성
        data = request.get_json()
        user_info = data.get('data')
        user_info = json.dumps(user_info, ensure_ascii=False) # <-- json 형식으로 변환

    # 여기서 user_info를 처리하는 로직을 작성합니다.
    # user_info.json 파일 내용을 업데이트하는 로직을 작성합니다.
    # 기존 파일 내용을 user_info로 덮어씌우면 됩니다.
    with open("./json_data/user_info.json", 'w', encoding="utf-8") as file:
        file.write(user_info)
    return {'status': 'success', 'message': '사용자 정보 업데이트 성공'}

# gpt_recommend을 gpt에게 질문한 뒤 답변을 리턴
@app.route('/gpt-recommend', methods=['POST'])
def gpt_recommend():
    if request.method == 'POST':
        
        # POST 메서드로 들어온 요청에 대한 처리 로직 작성
        with open("./json_data/user_info.json", 'r', encoding="utf-8") as file:
            user_data = json.load(file)


        # 파일에 변경 사항 저장
        with open("./json_data/user_info.json", 'w', encoding="utf-8") as file:
            json.dump(user_data, file, ensure_ascii=False, indent=4)
        

        if "learning_courses" in user_data and user_data["learning_courses"]:
            response = after_lesson_recommend_lessons()
        else:
            user_data["learning_courses"] = []
             # 파일에 변경 사항 저장
            with open("./json_data/user_info.json", 'w', encoding="utf-8") as file:
                json.dump(user_data, file, ensure_ascii=False, indent=4)

            response = initially_recommend_lessons()
    else:
        return 'Method Not Allowed', 405

    return {'gpt_recommend': response} 


# 서버에서 site_lecture_data를 읽어서 xp를 반환함
@app.route('/get-lecture-xp', methods=['POST'])
def get_lecture_xp():
    # 해당 lectuer의 xp 반환
    lecture_title = request.get_json().get('data')
    
    with open("./json_data/site_lecture_data.jsonl", 'r', encoding="utf-8") as file:
        for line in file:
            lecture = json.loads(line)
            if lecture['title'] == lecture_title:
                return {'status' : 200, 'lecture_xp': lecture['lecture_xp']}
        return {'status' : 400, 'lecture_xp': 0}

if __name__ == '__main__':
    app.run(debug=True)
