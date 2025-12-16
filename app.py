import streamlit as st
import pandas as pd
import auth
import data_manager
import time
import io
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="신성EP 개발 샘플 통합 시스템",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Try loading CSS, ignore if file not found yet (will be created)
try:
    local_css("styles.css")
except:
    pass

def get_status_color(status):
    """진행상태에 따른 색상 반환"""
    status_str = str(status).lower()
    # 접수 / 자재준비 / 생산중 / 출하준비 / 출하완료
    if '접수' in status_str:
        return '#fbbf24'  # 노란색
    elif '자재준비' in status_str:
        return '#3b82f6'  # 파란색
    elif '생산중' in status_str:
        return '#10b981'  # 초록색
    elif '출하준비' in status_str:
        return '#f59e0b'  # 주황색
    elif '출하완료' in status_str or '완료' in status_str:
        return '#22c55e'  # 밝은 초록색 (완료)
    else:
        return '#94a3b8'  # 회색 (기본)

def get_progress_status(row):
    """
    날짜/진행 정보를 기반으로 진행상태 기본값 계산
    - 출하일 있으면: 출하완료
    - 샘플완료일 있으면: 출하준비
    - 자재입고일 있으면: 생산중
    - 자재요청 또는 도면접수일 있으면: 자재준비
    - 그 외: 접수
    """
    # 출하완료
    if pd.notna(row.get('출하일')) and str(row.get('출하일')) not in ['', 'nan', 'NaT']:
        return '출하완료'
    # 출하준비 (샘플완료까지 끝난 상태)
    if pd.notna(row.get('샘플완료일')) and str(row.get('샘플완료일')) not in ['', 'nan', 'NaT']:
        return '출하준비'
    # 생산중 (자재입고 이후)
    if pd.notna(row.get('자재입고일')) and str(row.get('자재입고일')) not in ['', 'nan', 'NaT']:
        return '생산중'
    # 자재준비 (자재요청 또는 도면접수)
    if (
        pd.notna(row.get('자재요청')) and str(row.get('자재요청')) not in ['', 'nan', 'NaT']
    ) or (
        pd.notna(row.get('도면접수일')) and str(row.get('도면접수일')) not in ['', 'nan', 'NaT']
    ):
        return '자재준비'
    # 기본값: 접수
    return '접수'

def is_overdue(row):
    """납기가 지났는지 확인"""
    if '납기일' not in row.index:
        return False
    try:
        due_date_str = str(row['납기일'])
        if not due_date_str or due_date_str == 'nan' or due_date_str == 'NaT':
            return False
        
        # 날짜 파싱
        if isinstance(row['납기일'], pd.Timestamp):
            due_date = row['납기일'].date()
        else:
            due_date = pd.to_datetime(due_date_str).date()
        
        today = datetime.now().date()
        
        # 납기가 지났고 완료되지 않은 경우
        if due_date < today:
            # 출하일이 있으면 완료로 간주
            if pd.notna(row.get('출하일')) and str(row.get('출하일')) not in ['', 'nan', 'NaT']:
                return False
            return True
    except:
        pass
    return False

def style_dataframe(df):
    """데이터프레임에 색상 스타일 적용하여 HTML로 반환"""
    if df.empty:
        return df
    
    # 진행상태 계산 (날짜 필드 기반)
    if '진행상태' not in df.columns:
        df['진행상태'] = df.apply(get_progress_status, axis=1)
    
    # 진행상태 컬럼에 색상 배경 적용
    def style_status(val):
        color = get_status_color(val)
        return f'background-color: {color}; color: white; font-weight: bold; padding: 5px; border-radius: 4px; text-align: center;'
    
    # 납기 지난 항목 체크
    overdue_mask = df.apply(is_overdue, axis=1)
    
    # 스타일 적용
    styled_df = df.style.applymap(style_status, subset=['진행상태'])
    
    # 납기 지난 행에 빨간색 텍스트 적용
    def highlight_overdue(row):
        if overdue_mask[row.name]:
            return ['color: #dc2626; font-weight: bold;'] * len(row)
        return [''] * len(row)
    
    styled_df = styled_df.apply(highlight_overdue, axis=1)
    
    return styled_df

def login_page():
    st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.image("logo.png", width=300)
            st.markdown("""
            <div class="login-container">
                <h3 style='font-size: 1.8rem; margin-bottom: 2rem;'>
                    개발샘플 관리시스템
                </h3>
            </div>
            """, unsafe_allow_html=True)
        
        # 로그인/회원가입 탭
        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("아이디 (ID)", placeholder="아이디를 입력하세요")
                password = st.text_input("비밀번호 (Password)", type="password", placeholder="******")
                
                submit = st.form_submit_button("로그인 (Login)", use_container_width=True)
                
                if submit:
                    user = auth.login(username, password)
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user_info"] = user
                        st.session_state["current_username"] = username
                        st.success(f"환영합니다, {user['name']}님!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
        
        with tab2:
            st.info("💡 고객사 계정으로 회원가입하실 수 있습니다.")
            with st.form("register_form"):
                username = st.text_input("아이디 (ID)", placeholder="사용할 아이디를 입력하세요")
                password = st.text_input("비밀번호 (Password)", type="password", placeholder="비밀번호를 입력하세요")
                password_confirm = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")
                company = st.text_input("업체명", placeholder="회사명을 입력하세요")
                name = st.text_input("이름", placeholder="이름을 입력하세요")
                
                submit = st.form_submit_button("회원가입", use_container_width=True)
                
                if submit:
                    if password != password_confirm:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        success, message = auth.register_user(username, password, company, name)
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)

def dashboard_page(user):
    # Top Bar
    c1, c2 = st.columns([8, 2])
    with c1:
        st.title(f"📊 개발 샘플 현황 대장")
    with c2:
        st.write(f"접속자: **{user['name']}** ({user['company']})")
        col_logout, col_pw = st.columns(2)
        with col_logout:
            if st.button("로그아웃"):
                auth.logout()
        with col_pw:
            if st.button("비밀번호 변경"):
                st.session_state["show_password_change"] = True
    
    # 비밀번호 변경 모달
    if st.session_state.get("show_password_change", False):
        with st.expander("비밀번호 변경", expanded=True):
            with st.form("change_password_form"):
                old_password = st.text_input("현재 비밀번호", type="password")
                new_password = st.text_input("새 비밀번호", type="password")
                new_password_confirm = st.text_input("새 비밀번호 확인", type="password")
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submit = st.form_submit_button("변경", use_container_width=True)
                with col_cancel:
                    if st.form_submit_button("취소", use_container_width=True):
                        st.session_state["show_password_change"] = False
                        st.rerun()
                
                if submit:
                    if new_password != new_password_confirm:
                        st.error("새 비밀번호가 일치하지 않습니다.")
                    else:
                        # 현재 로그인한 사용자의 아이디 찾기
                        current_username = None
                        users = auth.load_users()
                        for username, user_info in users.items():
                            if user_info.get('name') == user['name'] and user_info.get('company') == user['company']:
                                current_username = username
                                break
                        
                        if current_username:
                            success, message = auth.change_password(
                                current_username,
                                old_password,
                                new_password
                            )
                            if success:
                                st.success(message)
                                st.session_state["show_password_change"] = False
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("사용자 정보를 찾을 수 없습니다.")

    st.markdown("---")

    # Data Handling
    df = data_manager.get_filtered_data(user["role"], user["company"])

    # --- CLIENT VIEW ---
    if user["role"] == "client":
        tab1, tab2 = st.tabs(["📋 내 요청 목록", "➕ 새 샘플 요청"])
        
        with tab1:
            st.info("💡 요청하신 샘플의 진행 현황을 실시간으로 확인하실 수 있습니다. 관리자가 입력한 자재요청 및 비고 사항도 확인하실 수 있습니다.")
            if not df.empty:
                # 고객사 화면에서도 모든 컬럼 표시 (자재요청, 비고 포함)
                display_df = df.copy()
                
                # 자재요청과 비고 컬럼이 있는지 확인하고 표시
                styled_df = style_dataframe(display_df)
                # 스타일링된 데이터프레임을 HTML로 변환하여 표시
                html = styled_df.to_html(escape=False)
                st.markdown(
                    f'<div style="overflow-x: auto; max-height: 600px; overflow-y: auto;">{html}</div>',
                    unsafe_allow_html=True
                )
                
                # 자재요청과 비고 필드 안내
                if "자재요청" in df.columns or "비고" in df.columns:
                    st.caption("📝 자재요청 및 비고는 관리자가 입력한 내용입니다.")
            else:
                st.warning("아직 요청 내역이 없습니다.")

        with tab2:
            st.subheader("새로운 샘플 개발 요청")
            with st.form("new_request"):
                # Row 1: 담당자 정보
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    req_name = st.text_input("담당자", value=user["name"])
                with col_u2:
                    dept = st.text_input("부서")

                st.markdown("---")
                
                # Row 2: 제품 정보
                c_1, c_2 = st.columns(2)
                with c_1:
                    project = st.text_input("차종")
                    part_name = st.text_input("품명")
                    part_number = st.text_input("품번")
                    delivery_place = st.text_input("납품장소")
                with c_2:
                    qty = st.number_input("요청수량", min_value=1, value=10)
                    target_date = st.date_input("납기일")
                    remarks = st.text_area("요청사항")
                
                st.markdown("---")
                
                # 파일 업로드 (폼 안에서 사용 가능하도록 key 추가)
                uploaded_file = st.file_uploader(
                    "첨부파일 (도면, 사양서 등)", 
                    type=['pdf', 'jpg', 'jpeg', 'png', 'xlsx', 'xls', 'pptx', 'ppt', 'doc', 'docx', 'zip', 'dwg'],
                    help="도면, 사양서, 이미지 등을 업로드할 수 있습니다.",
                    key="new_request_file"
                )
                
                # 파일이 업로드되었을 때 미리보기 표시
                if uploaded_file is not None:
                    st.info(f"📎 선택된 파일: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

                submitted = st.form_submit_button("요청 등록", type="primary")
                
                if submitted:
                    if not project or not part_name:
                        st.error("차종과 품명은 필수 입력입니다.")
                    else:
                        file_name = ""
                        # 폼 제출 시점에 파일 저장
                        if uploaded_file is not None:
                            try:
                                # 파일 저장 디렉토리 생성
                                import os
                                save_dir = "attachments"
                                if not os.path.exists(save_dir):
                                    os.makedirs(save_dir)
                                
                                # 타임스탬프와 원본 파일명을 조합하여 저장
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                # 파일명에 특수문자 제거
                                safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in "._- ")
                                file_name = f"{timestamp}_{safe_filename}"
                                file_path = os.path.join(save_dir, file_name)
                                
                                # 파일 저장
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                st.success(f"파일 저장 완료: {uploaded_file.name}")
                            except Exception as e:
                                st.warning(f"파일 저장 중 오류 발생: {e}. 요청은 등록되지만 파일은 저장되지 않았습니다.")
                        
                        new_data = {
                            "담당자": req_name,
                            "부서": dept,
                            "업체명": user["company"],
                            "차종": project,
                            "품명": part_name,
                            "품번": part_number,
                            "납품장소": delivery_place,
                            "요청수량": qty,
                            "납기일": target_date.strftime("%Y-%m-%d"),
                            "요청사항": remarks,
                            "첨부파일": file_name
                        }
                        if data_manager.add_request(new_data):
                            st.success("요청이 성공적으로 등록되었습니다.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("저장 중 오류가 발생했습니다.")

    # --- ADMIN VIEW ---
    else:
        st.info("🔧 관리자 모드: 모든 고객사의 요청 내역을 확인하고 관리할 수 있습니다.")
        
        # Tools
        co1, co2, co3 = st.columns([1, 1, 4])
        with co1:
             if st.button("🔄 데이터 새로고침"):
                 st.rerun()
        with co2:
            if not df.empty:
                # Use BytesIO for Excel download
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                processed_data = output.getvalue()
                
                st.download_button(
                    "📥 엑셀 다운로드",
                    data=processed_data,
                    file_name="sample_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key='download-xlsx'
                )

        # --- Mini Dashboard ---
        if not df.empty:
            st.markdown("### 📈 전체 현황 요약")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("총 요청 건수", f"{len(df)}건")
            with m2:
                # 진행상태 계산 (없으면 기본값 생성)
                if '진행상태' not in df.columns:
                    df['진행상태'] = df.apply(get_progress_status, axis=1)
                # 진행/대기: 접수, 자재준비, 생산중, 출하준비
                pending_mask = df['진행상태'].astype(str).isin(['접수', '자재준비', '생산중', '출하준비'])
                pending_count = pending_mask.sum()
                st.metric("진행/대기 중", f"{pending_count}건")
            with m3:
                # 완료: 출하완료
                completed_count = len(df[df['진행상태'].astype(str).str.contains('출하완료', na=False)])
                st.metric("완료 건수", f"{completed_count}건")
            with m4:
                company_count = df['업체명'].nunique()
                st.metric("참여 업체", f"{company_count}개사")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Charts Row
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.caption("진행상태별 현황")
                if '진행상태' not in df.columns:
                    df['진행상태'] = df.apply(get_progress_status, axis=1)
                status_counts = df['진행상태'].value_counts()
                st.bar_chart(status_counts, color="#3b82f6")
                
            with c2:
                st.caption("업체별 요청 건수")
                company_counts = df['업체명'].value_counts().head(5) # Top 5
                st.bar_chart(company_counts, color="#ef4444")
                
            with c3:
                st.caption("차종별 분포")
                if '차종' in df.columns:
                    project_counts = df['차종'].value_counts().head(5) # Top 5
                    st.bar_chart(project_counts, color="#10b981")
                
            st.divider()

        # Editable Dataframe for easy management
        st.subheader("통합 관리 대장")
        if not df.empty:
            # 스타일링된 미리보기 추가
            with st.expander("📊 스타일링된 뷰 (읽기 전용)", expanded=False):
                styled_df = style_dataframe(df)
                html = styled_df.to_html(escape=False)
                st.markdown(
                    f'<div style="overflow-x: auto; max-height: 600px; overflow-y: auto;">{html}</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            # Add a selection column for deletion
            # We create a copy to avoid SettingWithCopy warning on the original cached df if any
            display_df = df.copy()
            if "선택" not in display_df.columns:
                display_df.insert(0, "선택", False)

            # ---- 컬럼 타입 정리 (에디터용 뷰에만 적용) ----
            # 1) 날짜 컬럼: datetime 타입으로 변환 (캘린더 선택 가능하도록)
            date_columns = ["접수일", "납기일", "도면접수일", "완료예정일", "자재입고일", "샘플완료일", "출하일"]
            for col in date_columns:
                if col in display_df.columns:
                    try:
                        # 빈 값 처리
                        display_df[col] = display_df[col].replace(['', 'nan', 'None', None], pd.NaT)
                        # datetime 타입으로 변환 (날짜만, 시간 없음)
                        display_df[col] = pd.to_datetime(display_df[col], errors='coerce')
                    except Exception:
                        pass

            # 2) 텍스트 컬럼: 문자 입력 가능하도록 전부 문자열 타입으로 캐스팅
            text_columns = ["납품장소", "요청사항", "자재요청", "비고"]
            for col in text_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].astype("string").fillna("")

            # column_config 설정 (캘린더 선택 가능하도록)
            column_config = {
                "선택": st.column_config.CheckboxColumn(
                    "삭제 선택",
                    help="삭제할 항목을 선택하세요",
                    default=False,
                )
            }
            
            # 날짜 컬럼에 DateColumn 설정 (캘린더로 선택 가능)
            for col in date_columns:
                if col in display_df.columns:
                    # datetime 타입인 경우에만 DateColumn 설정
                    if pd.api.types.is_datetime64_any_dtype(display_df[col].dtype):
                        column_config[col] = st.column_config.DateColumn(
                            col,
                            help=f"{col}을 달력에서 선택하세요",
                            format="YYYY-MM-DD",
                        )

            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                height=600,
                num_rows="dynamic",
                key="admin_editor",
                column_config=column_config
            )
            
            col_act1, col_act2 = st.columns([1, 4])
            
            with col_act1:
                # Calculate selected items
                selected_rows = edited_df[edited_df["선택"] == True]
                
                if not selected_rows.empty:
                    if st.button(f"🗑️ 선택된 {len(selected_rows)}건 삭제", type="primary"):
                        ids_to_delete = selected_rows["관리번호"].tolist()
                        if data_manager.delete_requests_by_ids(ids_to_delete):
                             st.success(f"{len(selected_rows)}건이 삭제되었습니다.")
                             time.sleep(1)
                             st.rerun()
                        else:
                             st.error("삭제 중 오류가 발생했습니다.")
                
            with col_act2:
                # Save changes button (for other edits)
                if st.button("변경된 내용 저장"):
                    # Remove the '선택' column before saving
                    save_df = edited_df.drop(columns=["선택"], errors='ignore')
                    if data_manager.save_data(save_df):
                        st.success("데이터가 성공적으로 업데이트되었습니다.")
                    else:
                        st.error("저장 실패.")
            
            # 관리자 모드: 첨부파일 업로드 기능
            st.markdown("---")
            st.subheader("📎 첨부파일 업로드")
            st.info("특정 요청건에 첨부파일을 추가할 수 있습니다.")
            
            # 관리번호 선택 및 파일 업로드
            col_file1, col_file2 = st.columns([2, 3])
            with col_file1:
                if not df.empty:
                    request_ids = df['관리번호'].tolist()
                    selected_id = st.selectbox(
                        "관리번호 선택",
                        options=request_ids,
                        help="첨부파일을 추가할 요청건을 선택하세요"
                    )
                else:
                    selected_id = None
                    st.info("요청건이 없습니다.")
            
            with col_file2:
                admin_uploaded_file = st.file_uploader(
                    "첨부파일 업로드",
                    type=['pdf', 'jpg', 'jpeg', 'png', 'xlsx', 'xls', 'pptx', 'ppt', 'doc', 'docx', 'zip', 'dwg'],
                    help="도면, 사양서, 이미지 등을 업로드할 수 있습니다.",
                    key="admin_file_upload"
                )
            
            if selected_id and admin_uploaded_file is not None:
                if st.button("파일 업로드 및 저장", type="primary"):
                    try:
                        # 파일 저장 디렉토리 생성
                        import os
                        save_dir = "attachments"
                        if not os.path.exists(save_dir):
                            os.makedirs(save_dir)
                        
                        # 타임스탬프와 원본 파일명을 조합하여 저장
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        safe_filename = "".join(c for c in admin_uploaded_file.name if c.isalnum() or c in "._- ")
                        file_name = f"{timestamp}_{safe_filename}"
                        file_path = os.path.join(save_dir, file_name)
                        
                        # 파일 저장
                        with open(file_path, "wb") as f:
                            f.write(admin_uploaded_file.getbuffer())
                        
                        # 데이터베이스 업데이트
                        df_to_update = data_manager.load_data()
                        if selected_id in df_to_update['관리번호'].values:
                            idx = df_to_update.index[df_to_update['관리번호'] == selected_id].tolist()[0]
                            # 기존 첨부파일이 있으면 추가 (쉼표로 구분)
                            existing_file = str(df_to_update.at[idx, '첨부파일']) if '첨부파일' in df_to_update.columns else ""
                            if existing_file and existing_file.strip() != "" and existing_file != "nan":
                                df_to_update.at[idx, '첨부파일'] = f"{existing_file}, {file_name}"
                            else:
                                df_to_update.at[idx, '첨부파일'] = file_name
                            
                            if data_manager.save_data(df_to_update):
                                st.success(f"파일이 성공적으로 업로드되었습니다: {admin_uploaded_file.name}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("데이터베이스 업데이트 실패.")
                        else:
                            st.error("선택한 관리번호를 찾을 수 없습니다.")
                    except Exception as e:
                        st.error(f"파일 업로드 중 오류 발생: {e}")

        else:
            st.info("데이터가 없습니다.")
            
        # File Upload for Bulk Update
        st.markdown("---")
        st.subheader("📂 엑셀 일괄 업로드")
        uploaded_file = st.file_uploader("기존 엑셀파일을 업로드하여 데이터를 병합합니다.", type=['xlsx'])
        if uploaded_file:
            if st.button("업로드 및 병합"):
                try:
                    new_df = pd.read_excel(uploaded_file)
                    if data_manager.merge_data(new_df):
                        st.success("데이터가 성공적으로 병합되었습니다.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("데이터 병합 중 오류가 발생했습니다.")
                except Exception as e:
                    st.error(f"파일 처리 오류: {e}")

# Main Routing
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

user = auth.check_auth()

if user:
    dashboard_page(user)
else:
    login_page()
