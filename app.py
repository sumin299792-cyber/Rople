import streamlit as st
import random

# --- 1. 초기 설정 및 데이터 ---

# 던전 이벤트 목록 및 기본 몬스터 데이터
BASE_MONSTER = {"name": "슬라임", "hp": 20, "damage": 5, "xp": 10}
EVENTS = {
    'treasure': {"name": "보물 상자", "gold": 20},
    'trap': {"name": "함정", "damage": 10},
    'rest': {"name": "안전한 캠프", "heal": 15},
}

# --- 2. 게임 상태 초기화 및 재설정 ---
def initialize_game():
    """게임의 초기 상태를 세션 상태에 설정합니다. (단 한 번만 실행)"""
    if 'initialized' not in st.session_state:
        st.session_state.player_hp = 100
        st.session_state.player_max_hp = 100
        st.session_state.player_attack = 15
        st.session_state.player_gold = 50
        st.session_state.player_xp = 0
        st.session_state.level = 1
        st.session_state.story = "당신은 던전 입구에 서 있습니다. 모험을 시작하시겠습니까?"
        st.session_state.current_state = 'explore'  # explore, fight, shop, game_over
        st.session_state.current_enemy = None
        st.session_state.initialized = True
        st.session_state.monster_max_hp = 0 # 몬스터 최대 HP 저장을 위한 변수 추가

def reset_game():
    """모든 세션 상태를 삭제하고 앱을 재실행합니다."""
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
        
        st.markdown("---")
        if st.button("🔄 게임 재시작", help="모든 진행 상황을 초기화합니다."):
            reset_game()

# --- 4. 레벨업 시스템 ---
def check_level_up(xp_gained):
    """경험치를 추가하고 레벨업을 확인합니다."""
    st.session_state.player_xp += xp_gained
    
    xp_to_next_level = st.session_state.level * 50
    
    if st.session_state.player_xp >= xp_to_next_level:
        st.session_state.player_xp -= xp_to_next_level
        st.session_state.level += 1
        st.session_state.player_max_hp += 10
        st.session_state.player_attack += 5
        st.session_state.player_hp = st.session_state.player_max_hp
        
        st.balloons()
        st.session_state.story = f"🎉 **레벨 업!** 당신은 레벨 {st.session_state.level}이 되었습니다! 능력치가 증가했습니다."
        return True
    return False

# --- 5. 이벤트 처리 함수 ---
def explore_dungeon():
    """랜덤 던전 이벤트 발생 및 처리"""
    if st.session_state.player_hp <= 0:
        st.session_state.story = "☠️ 당신은 쓰러졌습니다. 다시 시작 버튼을 눌러주세요."
        st.session_state.current_state = 'game_over'
        return

    event_type = random.choices(
        ['monster', 'treasure', 'trap', 'rest'], 
        weights=[50, 25, 15, 10], 
        k=1
    )[0]
    
    if event_type == 'monster':
        # 몬스터 조우 (몬스터의 레벨을 플레이어 레벨에 맞춰 강화)
        monster_hp = BASE_MONSTER["hp"] + (st.session_state.level * 5)
        monster_damage = BASE_MONSTER["damage"] + st.session_state.level
        monster_xp = BASE_MONSTER["xp"] + st.session_state.level * 2
        
        st.session_state.current_enemy = {
            "name": f"강화된 {BASE_MONSTER['name']}",
            "hp": monster_hp,
            "damage": monster_damage,
            "xp": monster_xp
        }
        st.session_state.monster_max_hp = monster_hp # 몬스터 최대 HP 저장
        st.session_state.current_state = 'fight'
        st.session_state.story = f"**{st.session_state.current_enemy['name']}**가 당신 앞을 가로막습니다! 전투를 준비하세요."
        
    elif event_type == 'treasure':
        gold_gained = EVENTS['treasure']['gold'] + random.randint(1, st.session_state.level * 5)
        st.session_state.player_gold += gold_gained
        st.session_state.story = f"✨ **{EVENTS['treasure']['name']}**를 발견했습니다! {gold_gained} 골드를 획득했습니다."

    elif event_type == 'trap':
        damage = EVENTS['trap']['damage']
        st.session_state.player_hp -= damage
        st.session_state.player_hp = max(0, st.session_state.player_hp)
        st.session_state.story = f"💥 **{EVENTS['trap']['name']}**을 밟았습니다! {damage} 피해를 입었습니다. (현재 HP: {st.session_state.player_hp})"

    elif event_type == 'rest':
        heal_amount = EVENTS['rest']['heal']
        st.session_state.player_hp = min(st.session_state.player_hp + heal_amount, st.session_state.player_max_hp)
        st.session_state.story = f"⛺ **{EVENTS['rest']['name']}**에서 휴식을 취했습니다. 체력이 {heal_amount} 회복되었습니다. (현재 HP: {st.session_state.player_hp})"
        
# --- 6. 전투 로직 ---
def fight_turn():
    """전투 버튼을 눌렀을 때 턴 처리"""
    enemy = st.session_state.current_enemy
    
    # 플레이어 공격력 범위 적용
    player_hit = random.randint(st.session_state.player_attack - 5, st.session_state.player_attack + 5)
    enemy['hp'] -= player_hit
    
    # 몬스터 처치 확인
    if enemy['hp'] <= 0:
        xp_gained = enemy['xp']
        gold_gained = random.randint(10, 30)
        st.session_state.player_gold += gold_gained
        
        st.session_state.story = (
            f"⚔️ 당신은 {enemy['name']}에게 {player_hit} 피해를 입히고 처치했습니다! "
            f"+{xp_gained} XP, +{gold_gained} 골드 획득."
        )
        st.session_state.current_state = 'explore'
        check_level_up(xp_gained)
        return

    # 몬스터 반격
    monster_hit = random.randint(enemy['damage'] - 2, enemy['damage'] + 2)
    st.session_state.player_hp -= monster_hit
    st.session_state.player_hp = max(0, st.session_state.player_hp)
    
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
    st.title("🛡️ 스트림릿 던전 탐험 시뮬레이터 (v2.0)")
    
    # 1. 게임 초기화
    initialize_game()
    
    # 2. 상태 표시 (사이드바)
    display_status()
    
    # 3. 스토리 영역
    st.subheader("📚 현재 상황")
    if st.session_state.current_state == 'game_over':
        st.error(st.session_state.story)
        st.markdown("다시 시작하려면 왼쪽 메뉴의 **'게임 재시작'** 버튼을 눌러주세요.")
        return 

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
        # 몬스터 체력 시각화 (개선된 부분: 초기 최대 HP를 사용)
        if enemy and st.session_state.monster_max_hp > 0:
            st.warning(f"⚔️ **전투 중:** {enemy['name']}")
            
            enemy_hp_ratio = enemy['hp'] / st.session_state.monster_max_hp
            st.progress(enemy_hp_ratio, text=f"몬스터 HP: {enemy['hp']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.button("💥 공격!", on_click=fight_turn, type="primary", use_container_width=True)
            with col2:
                if st.button("🏃 도망치기 (70% 성공)", use_container_width=True):
                    if random.random() < 0.7:
                        st.session_state.story = "성공적으로 도망쳤습니다!"
                        st.session_state.current_state = 'explore'
                    else:
                        st.session_state.story = f"도망에 실패했습니다! {enemy['name']}의 공격을 받았습니다."
                        fight_turn() 
                        
    elif st.session_state.current_state == 'shop':
        # 상점 상태
        st.subheader("💰 여관 상점")
        st.write(f"현재 골드: **{st.session_state.player_gold}**")
        
        # 상점 아이템 로직
        if st.session_state.player_gold >= 30:
            if st.button("강화 물약 (공격력 +5) - 30골드", use_container_width=True):
                st.session_state.player_gold -= 30
                st.session_state.player_attack += 5
                st.session_state.story = "공격력이 5 증가했습니다! 이제 더 강해졌습니다."
                st.rerun() # 상태가 바로 반영되도록 재실행

        if st.session_state.player_gold >= 50:
            if st.button("생명력 증강 (최대 HP +20) - 50골드", use_container_width=True):
                st.session_state.player_gold -= 50
                st.session_state.player_max_hp += 20
                st.session_state.player_hp += 20
                st.session_state.story = "최대 체력이 20 증가하고 현재 체력이 회복되었습니다!"
                st.rerun() 
            
        st.markdown("---")
        st.button("⬅️ 다시 던전으로", on_click=lambda: st.session_state.update(current_state='explore'), use_container_width=True)

# 메인 함수 실행
if __name__ == '__main__':
    main()
