import streamlit as st
import pandas as pd
import auth
import data_manager
import time
import io

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
        
        with st.form("login_form"):
            username = st.text_input("아이디 (ID)", placeholder="admin or client")
            password = st.text_input("비밀번호 (Password)", type="password", placeholder="******")
            
            submit = st.form_submit_button("로그인 (Login)", use_container_width=True)
            
            if submit:
                user = auth.login(username, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user_info"] = user
                    st.success(f"환영합니다, {user['name']}님!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

def dashboard_page(user):
    # Top Bar
    c1, c2 = st.columns([8, 2])
    with c1:
        st.title(f"📊 개발 샘플 현황 대장")
    with c2:
        st.write(f"접속자: **{user['name']}** ({user['company']})")
        if st.button("로그아웃"):
            auth.logout()

    st.markdown("---")

    # Data Handling
    df = data_manager.get_filtered_data(user["role"], user["company"])

    # --- CLIENT VIEW ---
    if user["role"] == "client":
        tab1, tab2 = st.tabs(["📋 내 요청 목록", "➕ 새 샘플 요청"])
        
        with tab1:
            st.info("💡 요청하신 샘플의 진행 현황을 실시간으로 확인하실 수 있습니다.")
            if not df.empty:
                st.dataframe(
                    df, 
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )
            else:
                st.warning("아직 요청 내역이 없습니다.")

        with tab2:
            st.subheader("새로운 샘플 개발 요청")
            with st.form("new_request"):
                # Row 1: Basic User Info (Auto-filled but editable or new fields)
                col_u1, col_u2, col_u3 = st.columns(3)
                with col_u1:
                    req_name = st.text_input("요청자", value=user["name"])
                with col_u2:
                    dept = st.text_input("요청부서")
                with col_u3:
                    contact = st.text_input("연락처")
                    
                # Row 2: Contact Info
                col_e1, col_e2 = st.columns([2, 1])
                with col_e1:
                    email = st.text_input("e-mail")
                with col_e2:
                    # Spacer or additional field
                    pass

                st.markdown("---")
                
                # Row 3: Product Info
                c_1, c_2 = st.columns(2)
                with c_1:
                    project = st.text_input("차종/프로젝트")
                    part_name = st.text_input("품명")
                    spec = st.text_input("규격")
                with c_2:
                    qty = st.number_input("수량", min_value=1, value=10)
                    target_date = st.date_input("납기 요청일")
                    remarks = st.text_area("비고/요청사항")
                
                # File uploader
                uploaded_file = st.file_uploader("첨부파일 (도면 등)", type=['pdf', 'jpg', 'png', 'xlsx', 'pptx', 'zip'])
                file_name = ""
                if uploaded_file is not None:
                     # For MVP, we might just store the filename string. 
                     # To actually save the file, we need a directory.
                     import os
                     save_dir = "attachments"
                     if not os.path.exists(save_dir):
                         os.makedirs(save_dir)
                     
                     # Save with timestamp to avoid duplicates
                     timestamp = time.strftime("%Y%m%d_%H%M%S")
                     file_name = f"{timestamp}_{uploaded_file.name}"
                     with open(os.path.join(save_dir, file_name), "wb") as f:
                         f.write(uploaded_file.getbuffer())

                submitted = st.form_submit_button("요청 등록", type="primary")
                
                if submitted:
                    if not project or not part_name:
                        st.error("프로젝트명과 품명은 필수 입력입니다.")
                    else:
                        new_data = {
                            "요청자": req_name,
                            "요청부서": dept,
                            "업체명": user["company"],
                            "이메일": email,
                            "연락처": contact,
                            "차종/프로젝트": project,
                            "품명": part_name,
                            "규격": spec,
                            "수량": qty,
                            "납기요청일": target_date.strftime("%Y-%m-%d"),
                            "비고": remarks,
                            "첨부": file_name
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
                pending_count = len(df[df['진행상태'].astype(str).str.contains('대기|접수', na=False)])
                st.metric("진행/대기 중", f"{pending_count}건")
            with m3:
                completed_count = len(df[df['진행상태'].astype(str).str.contains('완료', na=False)])
                st.metric("완료 건수", f"{completed_count}건")
            with m4:
                company_count = df['업체명'].nunique()
                st.metric("참여 업체", f"{company_count}개사")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Charts Row
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.caption("진행상태별 현황")
                status_counts = df['진행상태'].value_counts()
                st.bar_chart(status_counts, color="#3b82f6")
                
            with c2:
                st.caption("업체별 요청 건수")
                company_counts = df['업체명'].value_counts().head(5) # Top 5
                st.bar_chart(company_counts, color="#ef4444")
                
            with c3:
                st.caption("차종/프로젝트별 분포")
                project_counts = df['차종/프로젝트'].value_counts().head(5) # Top 5
                st.bar_chart(project_counts, color="#10b981")
                
            st.divider()

        # Editable Dataframe for easy management
        st.subheader("통합 관리 대장")
        if not df.empty:
            # Add a selection column for deletion
            # We create a copy to avoid SettingWithCopy warning on the original cached df if any
            display_df = df.copy()
            if "선택" not in display_df.columns:
                display_df.insert(0, "선택", False)
            
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                height=600,
                num_rows="dynamic",
                key="admin_editor",
                column_config={
                    "선택": st.column_config.CheckboxColumn(
                        "삭제 선택",
                        help="삭제할 항목을 선택하세요",
                        default=False,
                    ),
                    "진행상태": st.column_config.SelectboxColumn(
                        "진행상태",
                        help="현재 진행 상태를 선택하세요",
                        width="medium",
                        options=[
                            "접수대기",
                            "접수",
                            "자재준비",
                            "생산중",
                            "생산완료",
                            "납품중",
                            "납품완료"
                        ],
                        required=True,
                    )
                }
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
