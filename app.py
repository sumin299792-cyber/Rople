import streamlit as st
import random

# --- 1. 초기 설정 및 데이터 ---

# 던전 이벤트 목록
EVENTS = {
    'monster': {"name": "슬라임", "hp": 20, "damage": 5, "xp": 10},
    'treasure': {"name": "보물 상자", "gold": 20, "item_chance': 0.5},
    'trap': {"name": "함정", "damage": 10},
    'rest': {"name": "안전한 캠프", "heal": 15},
}

# --- 2. 게임 상태 초기화 ---
def initialize_game():
    """게임의 초기 상태를 세션 상태에 저장합니다."""
    # 게임 상태가 초기화되지 않았을 때만 실행
    if 'initialized' not in st.session_state:
        st.session_state.player_hp = 100
        st.session_state.player_max_hp = 100
        st.session_state.player_attack = 15
        st.session_state.player_gold = 50
        st.session_state.player_xp = 0
        st.session_state.level = 1
        st.session_state.story = "당신은 던전 입구에 서 있습니다. 모험을 시작하시겠습니까?"
        st.session_state.current_state = 'explore'  # explore, fight, shop
        st.session_state.current_enemy = None
        st.session_state.initialized = True

def reset_game():
    """모든 세션 상태를 삭제하고 게임을 재시작합니다."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- 3. 캐릭터 상태 표시 (사이드바) ---
def display_status():
    """플레이어의 현재 상태를 사이드바에 표시합니다."""
    with st.sidebar:
        st.header("👤 캐릭터 상태")
        st.markdown(f"**레벨:** {st.session_state.level}")
        st.markdown(f"**경험치 (XP):** {st.session_state.player_xp}")
        st.markdown(f"**공격력:** {st.session_state.player_attack}")
        st.markdown(f"**골드 💰:** {st.session_state.player_gold}")
        
        # 체력 바 표시
        st.metric(
            label="체력 (HP)", 
            value=f"{st.session_state.player_hp}/{st.session_state.player_max_hp}", 
            delta_color="off"
        )
        st.progress(st.session_state.player_hp / st.session_state.player_max_hp, text="HP")
        
        # 게임 재시작 버튼
        st.markdown("---")
        if st.button("🔄 게임 재시작", help="모든 진행 상황을 초기화합니다."):
            reset_game()

# --- 4. 레벨업 시스템 ---
def check_level_up(xp_gained):
    """경험치를 추가하고 레벨업을 확인합니다."""
    st.session_state.player_xp += xp_gained
    
    # 레벨업에 필요한 경험치 (예: 레벨 * 50)
    xp_to_next_level = st.session_state.level * 50
    
    if st.session_state.player_xp >= xp_to_next_level:
        st.session_state.player_xp -= xp_to_next_level
        st.session_state.level += 1
        st.session_state.player_max_hp += 10 # 최대 체력 증가
        st.session_state.player_attack += 5  # 공격력 증가
        st.session_state.player_hp = st.session_state.player_max_hp # 체력 완전 회복
        
        st.balloons() # 레벨업 축하 효과
        st.session_state.story = f"🎉 **레벨 업!** 당신은 레벨 {st.session_state.level}이 되었습니다! 최대 체력과 공격력이 증가했습니다."
        return True
    return False

# --- 5. 이벤트 처리 함수 ---
def explore_dungeon():
    """랜덤 던전 이벤트 발생 및 처리"""
    if st.session_state.player_hp <= 0:
        st.session_state.story = "☠️ 당신은 쓰러졌습니다. 다시 시작 버튼을 눌러주세요."
        st.session_state.current_state = 'game_over'
        return

    # 이벤트 확률: 몬스터 50%, 보물 25%, 함정 15%, 휴식 10%
    event_type = random.choices(
        ['monster', 'treasure', 'trap', 'rest'], 
        weights=[50, 25, 15, 10], 
        k=1
    )[0]
    
    event_data = EVENTS[event_type]
    
    if event_type == 'monster':
        # 몬스터 조우
        st.session_state.current_enemy = {
            "name": event_data["name"],
            "hp": event_data["hp"],
            "damage": event_data["damage"],
            "xp": event_data["xp"]
        }
        st.session_state.current_state = 'fight'
        st.session_state.story = f"**{st.session_state.current_enemy['name']}**가 당신 앞을 가로막습니다! 전투를 준비하세요."
        
    elif event_type == 'treasure':
        # 보물 상자 발견
        gold_gained = event_data['gold']
        st.session_state.player_gold += gold_gained
        st.session_state.story = f"✨ **{event_data['name']}**를 발견했습니다! {gold_gained} 골드를 획득했습니다."

    elif event_type == 'trap':
        # 함정 발동
        damage = event_data['damage']
        st.session_state.player_hp -= damage
        st.session_state.player_hp = max(0, st.session_state.player_hp)
        st.session_state.story = f"💥 **{event_data['name']}**을 밟았습니다! {damage} 피해를 입었습니다. (현재 HP: {st.session_state.player_hp})"

    elif event_type == 'rest':
        # 휴식 캠프
        heal_amount = event_data['heal']
        # 최대 체력 이상은 회복하지 않음
        st.session_state.player_hp = min(st.session_state.player_hp + heal_amount, st.session_state.player_max_hp)
        st.session_state.story = f"⛺ **{event_data['name']}**에서 휴식을 취했습니다. 체력이 {heal_amount} 회복되었습니다. (현재 HP: {st.session_state.player_hp})"
        
# --- 6. 전투 로직 ---
def fight_turn():
    """전투 버튼을 눌렀을 때 턴 처리"""
    enemy = st.session_state.current_enemy
    
    # 1. 플레이어 공격
    player_hit = random.randint(st.session_state.player_attack - 5, st.session_state.player_attack + 5)
    enemy['hp'] -= player_hit
    
    # 몬스터 처치 확인
    if enemy['hp'] <= 0:
        xp_gained = enemy['xp']
        gold_gained = random.randint(10, 30)
        st.session_state.player_gold += gold_gained
        
        # 스토리 업데이트 및 상태 변경
        st.session_state.story = (
            f"⚔️ 당신은 {enemy['name']}에게 {player_hit} 피해를 입히고 처치했습니다! "
            f"+{xp_gained} XP, +{gold_gained} 골드 획득."
        )
        st.session_state.current_state = 'explore' # 전투 종료 후 탐험 상태로 복귀
        
        # 레벨업 확인
        check_level_up(xp_gained)
        return

    # 2. 몬스터 반격
    monster_hit = random.randint(enemy['damage'] - 2, enemy['damage'] + 2)
    st.session_state.player_hp -= monster_hit
    st.session_state.player_hp = max(0, st.session_state.player_hp) # 체력 0 미만 방지
    
    # 플레이어 사망 확인
    if st.session_state.player_hp <= 0:
        st.session_state.story = f"💀 {enemy['name']}의 반격에 {monster_hit} 피해를 입고 쓰러졌습니다... 게임 오버."
        st.session_state.current_state = 'game_over'
        return

    # 전투 진행 중 스토리 업데이트
    st.session_state.story = (
        f"당신은 {enemy['name']}에게 {player_hit} 피해를 입혔습니다. "
        f"몬스터의 반격으로 {monster_hit} 피해를 입었습니다. "
        f"(몬스터 HP: {enemy['hp']}, 당신 HP: {st.session_state.player_hp})"
    )


# --- 7. 메인 앱 로직 ---
def main():
    st.set_page_config(layout="centered")
    st.title("🛡️ 스트림릿 던전 탐험 시뮬레이터")
    
    # 1. 게임 초기화
    initialize_game()
    
    # 2. 상태 표시 (사이드바)
    display_status()
    
    # 3. 스토리 영역
    st.subheader("📚 현재 상황")
    if st.session_state.current_state == 'game_over':
        st.error(st.session_state.story)
        st.markdown("다시 시작하려면 왼쪽 메뉴의 '게임 재시작' 버튼을 눌러주세요.")
        return # 게임 오버 시 여기서 멈춤

    st.info(st.session_state.story)

    # 4. 행동 버튼 영역
    st.subheader("❓ 행동 선택")
    
    if st.session_state.current_state == 'explore':
        # 탐험 상태 버튼
        st.button("🌲 던전 깊숙이 탐험하기", on_click=explore_dungeon, type="primary", use_container_width=True)
        st.button("🏪 마을로 돌아가기 (상점)", on_click=lambda: st.session_state.update(current_state='shop'), use_container_width=True)
        
    elif st.session_state.current_state == 'fight':
        # 전투 상태 버튼
        enemy = st.session_state.current_enemy
        if enemy:
            st.warning(f"⚔️ **전투 중:** {enemy['name']} (HP: {enemy['hp']})")
            
            # 몬스터 체력 시각화 (RPG 느낌 강화)
            enemy_hp_ratio = enemy['hp'] / EVENTS['monster']['hp']
            st.progress(enemy_hp_ratio, text=f"몬스터 HP: {enemy['hp']}")
            
            col1, col2 = st.columns(2)
            with col1
