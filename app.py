import streamlit as st
import random

# --- 1. 게임 상태 초기화 함수 ---
def initialize_game():
    """게임의 초기 상태를 세션 상태에 저장합니다."""
    # st.session_state는 스트림릿 앱 내에서 변수 값을 유지하는 방법입니다.
    if 'health' not in st.session_state:
        st.session_state.health = 100
        st.session_state.max_health = 100
        st.session_state.gold = 50
        st.session_state.story = "용감한 모험가, 당신은 숲속 작은 마을에서 모험을 시작합니다."
        st.session_state.game_over = False

# --- 2. 게임 상태 표시 함수 ---
def display_status():
    """플레이어의 현재 상태를 사이드바에 표시합니다."""
    with st.sidebar:
        st.header("✨ 캐릭터 상태")
        
        # 체력 바 표시
        st.metric(label="체력 (HP)", value=f"{st.session_state.health}/{st.session_state.max_health}", delta_color="off")
        st.progress(st.session_state.health / st.session_state.max_health)
        
        # 골드 표시
        st.metric(label="골드 💰", value=st.session_state.gold)

# --- 3. 게임 이벤트 함수 ---

def encounter_monster():
    """몬스터와 조우했을 때의 이벤트입니다."""
    st.session_state.story = "당신은 덤불 속에서 사나운 **고블린**과 마주쳤습니다! 싸우시겠습니까?"
    st.session_state.current_action = 'fight'

def rest_in_town():
    """마을에서 휴식했을 때의 이벤트입니다."""
    if st.session_state.health < st.session_state.max_health:
        heal_amount = random.randint(10, 25)
        st.session_state.health = min(st.session_state.health + heal_amount, st.session_state.max_health)
        st.session_state.story = f"마을 여관에서 휴식을 취했습니다. 체력이 {heal_amount}만큼 회복되어 {st.session_state.health}가 되었습니다."
    else:
        st.session_state.story = "당신의 체력은 이미 가득 찼습니다. 다음 모험을 준비하세요!"
    st.session_state.current_action = 'explore' # 다음 행동은 다시 탐험으로

def fight_action():
    """전투 버튼을 눌렀을 때의 처리입니다."""
    if st.session_state.health <= 0:
        st.session_state.game_over = True
        return
        
    monster_damage = random.randint(5, 15)
    player_damage = random.randint(10, 20)
    
    st.session_state.health -= monster_damage
    
    # 전투 결과 스토리 업데이트
    if st.session_state.health <= 0:
        st.session_state.health = 0
        st.session_state.story = f"당신은 고블린에게 {monster_damage}의 피해를 입고 쓰러졌습니다... 게임 오버."
        st.session_state.game_over = True
    else:
        # 몬스터를 물리쳤다고 가정
        gold_gained = random.randint(10, 30)
        st.session_state.gold += gold_gained
        st.session_state.story = (
            f"당신은 고블린에게 {player_damage}의 피해를 입히고 물리쳤습니다! "
            f"승리 보상으로 {gold_gained} 골드를 획득했습니다. (현재 체력: {st.session_state.health})"
        )
    st.session_state.current_action = 'explore' # 전투 후에는 다시 탐험으로

# --- 4. 메인 앱 로직 ---
def main():
    st.title("⚔️ 스트림릿 텍스트 RPG (매우 단순)")
    
    # 게임 초기화
    initialize_game()
    
    # 상태 표시
    display_status()
    
    # 스토리 영역
    st.subheader("📚 현재 상황")
    st.info(st.session_state.story)
    
    # 게임 오버 처리
    if st.session_state.game_over:
        st.error("게임 오버! 다시 시작 버튼을 눌러주세요.")
        if st.button("🔄 다시 시작"):
            # 세션 상태를 초기화하고 앱을 다시 실행
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun() # 앱을 다시 실행
        return # 게임 오버 상태에서는 더 이상 버튼을 표시하지 않습니다.


    # --- 행동 선택 영역 ---
    st.subheader("❓ 다음 행동 선택")
    
    # 현재 행동 상태에 따라 다른 버튼 그룹 표시
    if st.session_state.get('current_action') == 'fight':
        # 전투 중일 때
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚔️ 싸우기", use_container_width=True):
                fight_action()
        with col2:
            st.button("🏃 도망치기 (구현 안됨)", disabled=True, use_container_width=True)
            
    else:
        # 탐험 상태일 때 (기본 상태)
        col1, col2, col3 = st.columns(3)
        with col1:
            # 주사위를 굴려 랜덤 이벤트를 발생시킵니다.
            if st.button("🌲 숲 탐험", use_container_width=True):
                # 70% 확률로 몬스터, 30% 확률로 발견
                if random.random() < 0.7: 
                    encounter_monster()
                else:
                    gold_found = random.randint(5, 15)
                    st.session_state.gold += gold_found
                    st.session_state.story = f"숲을 탐험하여 숨겨진 보물 상자에서 {gold_found} 골드를 발견했습니다!"
                    st.session_state.current_action = 'explore'
                
        with col2:
            if st.button("🏠 마을에서 휴식", use_container_width=True):
                rest_in_town()
                
        with col3:
             # 게임 종료 버튼
            if st.button("🚪 모험 끝내기", use_container_width=True):
                st.session_state.story = "당신은 모험을 마치고 평화로운 삶을 선택했습니다. 당신의 이야기는 여기서 끝납니다."
                st.session_state.game_over = True

# main 함수 실행
if __name__ == '__main__':
    # Streamlit은 앱의 모든 코드를 실행할 때마다 위에서부터 다시 실행하므로, 
    # st.session_state를 사용하여 게임 상태를 유지해야 합니다.
    main()
