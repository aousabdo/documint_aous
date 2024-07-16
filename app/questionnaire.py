import streamlit as st

def create_questionnaire(questions):
    responses = {}
    
    for question in questions:
        st.write(f"Question {question.id}: {question.text}")
        if question.user_hint:
            st.info(question.user_hint)
        
        if question.llm_hint:
            with st.expander(f"View Example Answer for Question {question.id}"):
                st.write(question.llm_hint)
        
        response = st.text_area(
            f"Your answer for Question {question.id} {'(Required)' if question.required else '(Optional)'}",
            key=f"question_{question.id}"
        )
        responses[question.id] = response

    if st.button("Submit Questionnaire", key="submit_questionnaire_button"):
        missing_required = [(q.id, q.text) for q in questions if q.required and not responses[q.id].strip()]
        if missing_required:
            st.error("Please fill in the following required fields:")
            for question_id, field in missing_required:
                st.error(f"Question {question_id}: {field}")
        else:
            return responses

    return None

def create_questionnaire_with_preload(questions):
    responses = {}
    
    for question in questions:
        responses[question.id] = question.llm_hint.replace("Example Answer ", "").strip()
        
    return responses