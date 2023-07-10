// background.js

const point = 80;
const apiURL_get_question = "http://localhost:5000/get_question";
const apiURL_check_answer = "http://localhost:5000/check_answer";

const apiURL_gpt_response = "http://localhost:5000/gpt-response";
const apiURL_gpt_recommend = "http://localhost:5000/gpt-recommend";
const signIn_response = "http://localhost:5000/sign-in";
const updateUserInfo = "http://localhost:5000/update-user-info";
const get_lecture_xp = "http://localhost:5000/get-lecture-xp";

// fetchData 함수 정의
function fetchData(url, request, sendResponse) {
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("서버 오류");
      }
    })
    .then((data) => {
      sendResponse(data);
    })
    .catch((error) => {
      console.error(error);
      sendResponse({ error: "서버 오류" });
    });
}

// 서버에서 GPT 답변을 받아옴
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "gpt-response") {
    fetchData(apiURL_gpt_response, request, sendResponse);
    return true;
  } else if (request.type === "sign-in") {
    fetchData(signIn_response, request, sendResponse);
    return true;
  } else if (request.type === "update-user-info") {
    fetchData(updateUserInfo, request, sendResponse);
    return true;
  } //add--recommend -> fetchData 함수로 수정해야 함
  else if (request.type === "gpt-recommend") {
    //커리큘럼 추천
    console.log("gpt-recommend");
    console.log(request);
    fetch(apiURL_gpt_recommend, {
      method: "POST", // POST 요청으로 수정
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request), // 요청 데이터를 JSON 형식으로 변환하여 전송
    })
      .then((response) => {
        console.log(response);
        if (response.ok) {
          console.log("response ok");
          return response.json();
        } else {
          console.log("response not ok");
          throw new Error("서버 오류");
        }
      })
      .then((data) => {
        console.log("data", data);
        sendResponse(data); // 응답 데이터를 전송
      })
      .catch((error) => {
        console.error(error);
        sendResponse({ error: "서버 오류" }); // 오류가 발생한 경우 에러 응답을 전송
      });

    return true; // 메시지 포트 유지를 위해 true 반환
  } else if (request.type === "request_question") {
    // 문제 번호
    const lectureName = request.lecture;

    // fetch API 이용
    fetch(`${apiURL_get_question}?lecture_name=${lectureName}`)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("서버 오류");
        }
      })
      .then((question) => {
        // content.js로 받아온 문제 전송
        console.log("문제를 성공적으로 받아왔습니다!", question);
        sendResponse({ question });
      })
      .catch((error) => {
        console.error(
          "문제를 받아오는 도중 오류가 발생했습니다:",
          error.message,
          error.name,
          error.stack
        );
        sendResponse({ error: "오류 발생" });
      });
    return true; // 메시지 포트 유지를 위해 true 반환
  } else if (request.type === "user_answer") {
    const questionId = request.questionId;
    const userAnswer = request.answer;
    const hasMoreChance = request.moreChance;

    // 사용자에게 전달할 정확도, 위즈의 해설 초기값
    const showUser = {
      accuracy: 10,
      message: "message",
    };

    fetch(`${apiURL_check_answer}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question_id: questionId, answer: userAnswer }),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          return response.json().then((errorData) => {
            throw new Error(
              `서버 오류: ${response.status} - ${response.statusText}, 오류 메시지: ${errorData.message}`
            );
          });
        }
      })
      .then((data) => {
        // if(data.similarity===0){

        //   const similarity = data.similarity; // 정확도
        //   const feedback = data.feedback; // 위즈의 해설

        //   showUser.accuracy = similarity;
        //   showUser.message = "정확도는 " + similarity + " 입니다. ";
        //   showUser.message+="틀렸습니다. 다시 시도해보세요";

        //   // 틀린것에 대한 힌트를 주고 싶다면
        //   // showUser.message+=feedback;

        //   sendResponse(showUser); // content.js로 결과 전송
        // }
        // else
        if (data.similarity!=undefined) {

          const similarity = data.similarity; // 정확도
          const feedback = data.feedback; // 위즈의 해설

          showUser.accuracy = similarity;
          showUser.message = "정확도는 " + similarity + " 입니다. ";

          if(similarity >= point ){
            showUser.message+=feedback;
          }
          else{
            showUser.message+="틀렸습니다. 다시 시도해보세요";
          // 틀린것에 대한 힌트를 주고 싶다면
          // showUser.message+=feedback;

          }
          sendResponse(showUser); // content.js로 결과 전송
        } else {
          throw new Error("점수를 받아오지 못했습니다.");
        }
      })
      .catch((error) => {
        console.error("오류 발생:", error.message, error.name, error.stack);
        sendResponse({ error: "오류 발생" });
      });

    return true; // 메시지 포트 유지를 위해 true 반환
  } else if (request.type === "get-lecture-xp") {
    //해당 강의의 xp를 가져옴
    console.log("gpt-lecture-xp");
    console.log(request);
    fetch(get_lecture_xp, {
      method: "POST", // GET 요청으로 수정
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request), // 요청 데이터를 JSON 형식으로 변환하여 전송
    })
      .then((response) => {
        console.log(response);
        if (response.status === 200) {
          console.log("response ok");
          return response.json();
        } else {
          console.log("response not ok");
          throw new Error("서버 오류");
        }
      })
      .then((data) => {
        console.log("data", data);
        sendResponse(data); // 응답 데이터를 전송
      })
      .catch((error) => {
        console.error(error);
        sendResponse({ error: "서버 오류" }); // 오류가 발생한 경우 에러 응답을 전송
      });

    return true; // 메시지 포트 유지를 위해 true 반환
  }
});
