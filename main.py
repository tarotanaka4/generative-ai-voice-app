import os
import time
from time import sleep
from pathlib import Path
import functions as func
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.markdown('## 生成AI英会話アプリ')

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.start_flg = False
    st.session_state.end_flg = False
    st.session_state.shadowing_flg = False
    st.session_state.shadowing_continue_flg = False
    st.session_state.shadowing_count = 0
    st.session_state.dictation_flg = False
    st.session_state.dictation_button_flg = False
    st.session_state.dictation_count = 0
    st.session_state.chat_wait_flg = False
    st.session_state.chat_count = 0
    st.session_state.chat_input_file_path = ""
    st.session_state.shadowing_state = False


    st.session_state.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    # LLMとのやり取り
    system_template = """
    You are a conversational English tutor. Engage in a natural and free-flowing conversation with the user. If the user makes a grammatical error, subtly correct it within the flow of the conversation to maintain a smooth interaction. Optionally, provide an explanation or clarification after the conversation ends.
    """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_template),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=500,
        return_messages=True
    )
    st.session_state.chain = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )

col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
with col1:
    if st.session_state.start_flg:
        st.button("英会話開始")
    else:
        st.session_state.start_flg = st.button("英会話開始")
with col2:
    if st.session_state.end_flg:
        st.button("一時中断")
    else:
        st.session_state.end_flg = st.button("一時中断")
with col3:
    st.session_state.speed = st.selectbox(label="再生速度", options=[2.0, 1.5, 1.2, 1.0, 0.8, 0.6], index=3, label_visibility="collapsed")
with col4:
    st.session_state.mode = st.selectbox(label="モード", options=["日常英会話", "シャドーイング", "ディクテーション"], label_visibility="collapsed")

with st.chat_message("assistant", avatar="images/370377.jpg"):
    # st.success("こちらは生成AIによる音声英会話の練習アプリです。何度も繰り返し練習して、英語力をアップさせましょう。")
    # st.markdown("")
    st.success("""
    - モードと再生速度を選択し、「英会話開始」ボタンを押して英会話を始めましょう。
    - モードは「日常英会話」「シャドーイング」「ディクテーション」から選べます。
    - 発話後、5秒間沈黙することで音声入力が完了します。
    - 「一時中断」ボタンを押すことで、英会話を一時中断できます。
    """)

if st.session_state.mode == "シャドーイング":
    if st.session_state.shadowing_flg:
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                with st.chat_message(message["role"], avatar="images/370377.jpg"):
                    st.markdown(message["content"])
            else:
                with st.chat_message(message["role"], avatar="images/23260507.jpg"):
                    st.markdown(message["content"])
        if not st.session_state.shadowing_continue_flg and not st.session_state.shadowing_state:
            st.stop()
if st.session_state.mode == "ディクテーション":
    if st.session_state.dictation_flg:
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                with st.chat_message(message["role"], avatar="images/370377.jpg"):
                    st.markdown(message["content"])
            else:
                with st.chat_message(message["role"], avatar="images/23260507.jpg"):
                    st.markdown(message["content"])
        st.session_state.dictation_button_flg = st.button("ディクテーション開始")


if st.session_state.end_flg:
    st.info("英会話を一時中断します。")
    st.session_state.messages = []
    st.session_state.start_flg = False
    st.session_state.end_flg = False
    st.session_state.shadowing_flg = False
    st.session_state.shadowing_continue_flg = False
    st.session_state.shadowing_count = 0
    st.session_state.dictation_flg = False
    st.session_state.dictation_button_flg = False
    st.session_state.dictation_count = 0
    st.session_state.chat_wait_flg = False
    st.session_state.chat_count = 0
    st.session_state.chat_input_file_path = ""
    st.session_state.shadowing_state = False

if st.session_state.chat_wait_flg:
    st.info("AIが読み上げた音声を、画面下部のチャット欄からそのまま入力・送信してください。")

chat_message = st.chat_input("※「ディクテーション」選択時以外は入力不可")

if not chat_message and st.session_state.chat_wait_flg:
    st.stop()

if st.session_state.start_flg:
    if st.session_state.mode == "ディクテーション" and (st.session_state.dictation_button_flg or st.session_state.dictation_count == 0 or chat_message):
        if not chat_message:
            with st.spinner('問題文生成中...'):
                system_template = """
                Generate 1 sentence that reflect natural English used in daily conversations, workplace, and social settings:
                - Casual conversational expressions
                - Polite business language
                - Friendly phrases used among friends
                - Sentences with situational nuances and emotions
                - Expressions reflecting cultural and regional contexts

                Limit your response to an English sentence of approximately 15 words.
                # Make each sentence 10-15 words long with clear and understandable context.
                """
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content=system_template),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template("{input}")
                ])
                llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
                memory = ConversationSummaryBufferMemory(
                    llm=llm,
                    max_token_limit=500,
                    return_messages=True
                )
                st.session_state.dictation_problem_chain = ConversationChain(
                    llm=llm,
                    prompt=prompt,
                    memory=memory
                )
                st.session_state.problem = st.session_state.dictation_problem_chain.predict(input="")
                # LLMからの回答を音声データに変換
                response = st.session_state.client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=st.session_state.problem
                )
                # mp3形式の音声ファイルをwav形式に変換して保存
                output_file_path = Path.cwd() / "audio/output" / f"recorded_audio_output_{int(time.time())}.wav"
                func.save_to_wav(response.content, output_file_path)
            # 音声ファイルの読み上げ
            func.play_wav(str(output_file_path), speed=st.session_state.speed, stop=True)

        if not chat_message:
            st.session_state.chat_wait_flg = True
            st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.problem})
            st.session_state.messages.append({"role": "user", "content": chat_message})
            with st.chat_message("assistant", avatar="images/370377.jpg"):
                st.markdown(st.session_state.problem)
            with st.chat_message("user", avatar="images/23260507.jpg"):
                st.markdown(chat_message)
            
            with st.spinner('評価結果の生成中...'):
                system_template = """
                あなたは英語学習の専門家です。
                以下の「LLMによる問題文」と「ユーザーによる回答文」を比較し、分析してください：

                【LLMによる問題文】
                問題文：{llm_text}

                【ユーザーによる回答文】
                回答文：{user_text}

                【分析項目】
                1. 単語の正確性（誤った単語、抜け落ちた単語、追加された単語）
                2. 文法的な正確性
                3. 文の完成度

                フィードバックは以下のフォーマットで日本語で提供してください：

                【評価】 # ここで改行を入れる
                ✓ 正確に再現できた部分 # 項目を複数記載
                △ 改善が必要な部分 # 項目を複数記載
                
                【アドバイス】 # ここで改行を入れる
                次回の練習のためのポイント

                ユーザーの努力を認め、前向きな姿勢で次の練習に取り組めるような励ましのコメントを含めてください。
                """
                system_template = system_template.format(
                    llm_text=st.session_state.problem,
                    user_text=chat_message
                )
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content=system_template),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template("{input}")
                ])
                llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
                memory = ConversationSummaryBufferMemory(
                    llm=llm,
                    max_token_limit=500,
                    return_messages=True
                )
                st.session_state.dictation_feedback_chain = ConversationChain(
                    llm=llm,
                    prompt=prompt,
                    memory=memory
                )
                result = st.session_state.dictation_feedback_chain.predict(input="")
            st.session_state.messages.append({"role": "assistant", "content": result})
            with st.chat_message("assistant", avatar="images/370377.jpg"):
                st.markdown(result)
            
            st.session_state.dictation_flg = True
            st.session_state.dictation_button_flg = True
            chat_message = ""
            st.session_state.dictation_count += 1
            st.session_state.chat_wait_flg = False
            st.rerun()

    if st.session_state.mode == "シャドーイング":
        system_template = """
        Generate 1 sentence that reflect natural English used in daily conversations, workplace, and social settings:
        - Casual conversational expressions
        - Polite business language
        - Friendly phrases used among friends
        - Sentences with situational nuances and emotions
        - Expressions reflecting cultural and regional contexts

        Make each sentence 20-30 words long with clear and understandable context.
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_template),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
        memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=500,
            return_messages=True
        )
        st.session_state.shadowing_problem_chain = ConversationChain(
            llm=llm,
            prompt=prompt,
            memory=memory
        )
        if st.session_state.shadowing_state == False:
            with st.spinner('問題文生成中...'):
                problem = st.session_state.shadowing_problem_chain.predict(input="")
                # st.session_state.messages.append({"role": "assistant", "content": problem})
            
                # LLMからの回答を音声データに変換
                response = st.session_state.client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=problem
                )
                # mp3形式の音声ファイルをwav形式に変換して保存
                output_file_path = Path.cwd() / "audio/output" / f"recorded_audio_output_{int(time.time())}.wav"
                func.save_to_wav(response.content, output_file_path)
            # 音声ファイルの読み上げ
            func.play_wav(str(output_file_path), speed=st.session_state.speed)

            st.session_state.shadowing_state = True
            st.session_state.shadowing_problem = problem
            st.button("問題が聞き取れたら次へ")
        else:
            # 音声入力の受け取り
            speech_file_path = func.record_audio()
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.shadowing_problem})

            st.session_state.shadowing_state = False

            with st.spinner('音声入力をテキストに変換中...'):
                # 音声入力をテキストに変換
                result = func.transcribe(speech_file_path, st.session_state.client)
                st.session_state.messages.append({"role": "user", "content": result.text})
                with st.chat_message("assistant", avatar="images/370377.jpg"):
                    st.markdown(st.session_state.shadowing_problem)
                with st.chat_message("user", avatar="images/23260507.jpg"):
                    st.markdown(result.text)

            with st.spinner('評価結果の生成中...'):
                system_template = """
                あなたは英語学習の専門家です。
                以下の「LLMによる問題文」と「ユーザーによる回答文」を比較し、分析してください：

                【LLMによる問題文】
                問題文：{llm_text}

                【ユーザーによる回答文】
                回答文：{user_text}

                【分析項目】
                1. 単語の正確性（誤った単語、抜け落ちた単語、追加された単語）
                2. 文法的な正確性
                3. 文の完成度

                フィードバックは以下のフォーマットで日本語で提供してください：

                【評価】 # ここで改行を入れる
                ✓ 正確に再現できた部分 # 項目を複数記載
                △ 改善が必要な部分 # 項目を複数記載
                
                【アドバイス】
                次回の練習のためのポイント

                ユーザーの努力を認め、前向きな姿勢で次の練習に取り組めるような励ましのコメントを含めてください。
                """
                system_template = system_template.format(
                    llm_text=st.session_state.shadowing_problem,
                    user_text=result.text
                )
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content=system_template),
                    MessagesPlaceholder(variable_name="history"),
                    HumanMessagePromptTemplate.from_template("{input}")
                ])
                st.session_state.shadowing_feedback_chain = ConversationChain(
                    llm=llm,
                    prompt=prompt,
                    memory=memory
                )
                result = st.session_state.shadowing_feedback_chain.predict(input="")
            st.session_state.messages.append({"role": "assistant", "content": result})
            with st.chat_message("assistant", avatar="images/370377.jpg"):
                st.markdown(result)
            
            st.session_state.shadowing_flg = True
            st.session_state.shadowing_count += 1
            st.session_state.messages = []
            st.session_state.shadowing_continue_flg = True
            st.button("シャドーイングを継続")
    if st.session_state.mode == "日常英会話":
        # 音声入力の受け取り
        if st.session_state.chat_count==0:
            st.session_state.chat_input_file_path = func.record_audio()
            st.session_state.chat_count=st.session_state.chat_count+1
            st.rerun()
        else:
            st.session_state.chat_count=st.session_state.chat_count+1
            for message in st.session_state.messages:
                if message["role"] == "assistant":
                    with st.chat_message(message["role"], avatar="images/370377.jpg"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message(message["role"], avatar="images/23260507.jpg"):
                        st.markdown(message["content"])

            # 音声入力をテキストに変換
            result = func.transcribe(st.session_state.chat_input_file_path, st.session_state.client)
            st.session_state.messages.append({"role": "user", "content": result.text})
            with st.chat_message("user", avatar="images/23260507.jpg"):
                st.markdown(result.text)

            result = st.session_state.chain.predict(input=result.text)
            st.session_state.messages.append({"role": "assistant", "content": result})
            with st.chat_message("assistant", avatar="images/370377.jpg"):
                st.markdown(result)

            # LLMからの回答を音声データに変換
            response = st.session_state.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=result
            )

            # mp3形式の音声ファイルをwav形式に変換して保存
            output_file_path = Path.cwd() / "audio/output" / f"recorded_audio_output_{int(time.time())}.wav"
            func.save_to_wav(response.content, output_file_path)

            # 音声ファイルの読み上げ
            func.play_wav(str(output_file_path), speed=st.session_state.speed)

            if st.session_state.chat_count>1:
                st.session_state.chat_input_file_path = func.record_audio()
            else:
                st.rerun()
