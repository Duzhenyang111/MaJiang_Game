import player_class
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_game_title():
    print("""\n
    日本麻将游戏
    =============
    """)

def print_game_rules():
    print("""\n日本麻将规则简介：
1. 游戏使用136张牌，包括万、条、筒（各36张）和字牌（28张）
2. 每位玩家初始获得13张牌
3. 轮流摸牌和打牌
4. 胡牌需要凑齐4组面子（刻子或顺子）和1对雀头
5. 刻子：三张相同的牌
6. 顺子：三张同花色连续的牌（仅限数牌）
7. 雀头：一对相同的牌
    """)

def print_menu():
    print("\n请选择：")
    print("1. 开始新游戏")
    print("2. 查看游戏规则")
    print("3. 退出游戏")
    return input("请输入选项（1-3）: ").strip()

def select_players():
    human_players = 0
    ai_players = 0
    total_players = 0
    show_ai_cards = False
    
    # 选择人类玩家数量
    while True:
        try:
            human_players = int(input("\n请选择人类玩家数量（1-4）: ").strip())
            if 1 <= human_players <= 4:
                break
            else:
                print("请输入1-4之间的数字！")
        except ValueError:
            print("请输入有效的数字！")
    
    # 选择AI玩家数量
    while True:
        try:
            ai_players = int(input(f"\n请选择AI玩家数量（0-{4-human_players}）: ").strip())
            if 0 <= ai_players <= (4-human_players):
                break
            else:
                print(f"请输入0-{4-human_players}之间的数字！")
        except ValueError:
            print("请输入有效的数字！")
    
    # 选择是否显示电脑牌信息
    if ai_players > 0:
        while True:
            choice = input("\n是否显示电脑牌信息？(y/n): ").strip().lower()
            if choice in ['y', 'n']:
                show_ai_cards = (choice == 'y')
                break
            else:
                print("请输入y或n！")
    
    return human_players, ai_players, show_ai_cards

def main():
    clear_screen()
    print_game_title()
    
    while True:
        choice = print_menu()
        
        if choice == '1':
            clear_screen()
            print_game_title()
            print("\n开始新游戏...")
            human_players, ai_players, show_ai_cards = select_players()
            game = player_class.MahjongGame(human_players=human_players, ai_players=ai_players, show_ai_cards=show_ai_cards)
            game.play()
            input("\n按Enter键返回主菜单...")
            clear_screen()
            print_game_title()
        
        elif choice == '2':
            clear_screen()
            print_game_title()
            print_game_rules()
            input("\n按Enter键返回主菜单...")
            clear_screen()
            print_game_title()
        
        elif choice == '3':
            print("\n感谢您的游玩，再见！")
            sys.exit(0)
        
        else:
            print("\n无效的选项，请重新选择！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n游戏被中断，感谢您的游玩！")
    # except Exception as e:
    #     print(f"\n游戏发生错误：{e}")
    #     input("按Enter键退出...")