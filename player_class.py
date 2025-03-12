import random
import os
from datetime import datetime

# 生成麻将牌
def generate_tiles():
    tiles = []
    for suit in ['m', 't', 'p']:
        for num in range(1, 10):
            tiles.extend([f"{num}{suit}"] * 4)
    for zi in ['e', 's', 'w', 'n', 'z', 'f', 'b']:
        tiles.extend([zi] * 4)
    random.shuffle(tiles)
    return tiles

# 排序手牌
def sort_hand(hand):
    def sort_key(tile):
        if tile[-1] in ['m', 't', 'p']:
            suit_order = {'m':0, 't':1, 'p':2}
            num = int(tile[:-1])
            return (suit_order[tile[-1]], num)
        else:
            zi_order = {'e':0, 's':1, 'w':2, 'n':3, 'z':4, 'f':5, 'b':6}
            return (3, zi_order.get(tile, 7))
    return sorted(hand, key=sort_key)

# 显示手牌
def display_hand(hand, player_name):
    sorted_hand = sort_hand(hand)
    current_type = None
    display_lines = []
    
    for tile in sorted_hand:
        if tile[-1] in ['m', 't', 'p']:
            suit = tile[-1]
            prefix = {'m': '万', 't': '条', 'p': '筒'}[suit]
            name = f"{tile[:-1]}{prefix}"
            tile_type = prefix
        else:
            zi_map = {'e':'东', 's':'南', 'w':'西', 'n':'北', 'z':'中', 'f':'发', 'b':'白'}
            name = f"{zi_map[tile]}"
            tile_type = '字牌'
        
        if tile_type != current_type:
            current_type = tile_type
            display_lines.append(f"\n{current_type}: ")
        
        display_lines[-1] += f"{name}({tile}) "
    
    print(f"{player_name}手牌：" + "".join(display_lines).strip())

class Player:
    def __init__(self, name, is_computer=False):
        self.hand = []
        self.name = name
        self.is_computer = is_computer
        self.discards = []
        self.melds = []  # 吃、碰、杠的组合

    def draw_tile(self, tile):
        self.hand.append(tile)

    def discard_tile(self, tile):
        self.hand.remove(tile)
        self.discards.append(tile)
        return tile

    def auto_discard(self):
        # 使用高级AI策略选择要丢弃的牌
        try:
            from ai_strategy import AdvancedAI
            discard_tile = AdvancedAI.select_discard_tile(self.hand)
            return self.discard_tile(discard_tile)
        except ImportError:
            # 如果高级AI模块不可用，使用简单策略
            sorted_hand = sort_hand(self.hand)
            
            # 统计各牌数量
            count = {}
            for tile in sorted_hand:
                count[tile] = count.get(tile, 0) + 1
            
            # 寻找孤张字牌
            for tile in sorted_hand:
                if tile in ['e','s','w','n','z','f','b'] and count[tile] == 1:
                    return self.discard_tile(tile)
            
            # 寻找边张（1和9）
            for tile in sorted_hand:
                if tile[-1] in ['m','t','p']:
                    num = int(tile[:-1])
                    if num == 1 or num == 9:
                        return self.discard_tile(tile)
            
            # 随机丢弃
            return self.discard_tile(random.choice(sorted_hand))
    
    def can_chi(self, tile, discarder_idx=None, current_idx=None):
        """检查是否可以吃牌"""
        # 只有数牌可以吃，且只能吃上家的牌
        if tile[-1] not in ['m', 't', 'p'] or discarder_idx is None or current_idx is None:
            return []
        
        # 检查是否为上家关系
        if (discarder_idx + 1) % 4 != current_idx:
            return []
            
        suit = tile[-1]
        num = int(tile[:-1])
        options = []
        
        # 检查是否有连续的牌可以吃
        # 例如，对于5m，检查是否有3m+4m, 4m+6m, 或6m+7m
        if num >= 3:
            if f"{num-2}{suit}" in self.hand and f"{num-1}{suit}" in self.hand:
                options.append([f"{num-2}{suit}", f"{num-1}{suit}", tile])
        
        if num >= 2 and num <= 8:
            if f"{num-1}{suit}" in self.hand and f"{num+1}{suit}" in self.hand:
                options.append([f"{num-1}{suit}", tile, f"{num+1}{suit}"])
        
        if num <= 7:
            if f"{num+1}{suit}" in self.hand and f"{num+2}{suit}" in self.hand:
                options.append([tile, f"{num+1}{suit}", f"{num+2}{suit}"])
        
        return options
    
    def can_peng(self, tile):
        """检查是否可以碰牌"""
        return self.hand.count(tile) >= 2
    
    def can_gang(self, tile):
        """检查是否可以杠牌"""
        return self.hand.count(tile) >= 3
    
    def can_self_gang(self):
        """检查是否可以自摸杠（包括暗杠和加杠）"""
        # 检查暗杠（手牌中有四张相同的牌）
        counts = {}
        for t in self.hand:
            counts[t] = counts.get(t, 0) + 1
        dark_gang = [t for t, count in counts.items() if count == 4]
        
        # 检查加杠（已经碰过的牌，手上有第四张）
        add_gang = []
        for meld_type, tiles in self.melds:
            if meld_type == 'peng':
                tile = tiles[0]  # 碰的三张牌都是相同的，取第一张
                if tile in self.hand:
                    add_gang.append(tile)
        
        return dark_gang + add_gang

    def perform_chi(self, tile, option):
        """执行吃牌操作"""
        # 移除手牌中用于吃的两张牌
        for t in option[:2]:  # 只移除前两张，第三张是被吃的牌
            if t in self.hand:  # 确保牌在手牌中
                self.hand.remove(t)
        
        # 添加吃的组合到玩家的面子中
        # 确保不重复添加被吃的牌
        if tile not in option:
            self.melds.append(('chi', option + [tile]))
        else:
            self.melds.append(('chi', option))
        
        return True
    
    def perform_peng(self, tile):
        """执行碰牌操作"""
        # 移除手牌中的两张相同牌
        for _ in range(2):
            self.hand.remove(tile)
        
        # 添加碰的组合到玩家的面子中
        self.melds.append(('peng', [tile, tile, tile]))
        
        return True
    
    def perform_gang(self, tile, is_self_gang=False, is_add_gang=False):
        """执行杠牌操作"""
        if is_add_gang:
            # 加杠，移除手牌中的一张牌，并将碰变成杠
            self.hand.remove(tile)
            for i, (meld_type, tiles) in enumerate(self.melds):
                if meld_type == 'peng' and tiles[0] == tile:
                    self.melds[i] = ('gang', [tile, tile, tile, tile])
                    break
        elif is_self_gang:
            # 暗杠，移除手牌中的四张相同牌
            for _ in range(4):
                self.hand.remove(tile)
            self.melds.append(('gang', [tile, tile, tile, tile]))
        else:
            # 明杠，移除手牌中的三张相同牌
            for _ in range(3):
                self.hand.remove(tile)
            self.melds.append(('gang', [tile, tile, tile, tile]))
        
        return True

class MahjongGame:
    def __init__(self, human_players=1, ai_players=3, show_ai_cards=False):
        # 确保总玩家数不超过4
        total_players = human_players + ai_players
        if total_players > 4:
            print("警告：总玩家数不能超过4，已自动调整")
            # 如果总数超过4，优先保留人类玩家
            if human_players > 4:
                human_players = 4
                ai_players = 0
            else:
                ai_players = 4 - human_players
        
        # 是否显示电脑牌的信息
        self.show_ai_cards = show_ai_cards
        
        self.tiles = generate_tiles()
        self.players = []
        
        # 创建人类玩家
        for i in range(human_players):
            player_name = f"玩家{i+1}" if human_players > 1 else "玩家"
            self.players.append(Player(player_name, is_computer=False))
        
        # 创建AI玩家
        for i in range(ai_players):
            self.players.append(Player(f"电脑{i+1}", is_computer=True))
        
        self.current_player = 0
        self.winner = None
        self.log = []
        self.last_discarded = None
        self.last_discarder = None
        
        # 初始发牌
        for _ in range(13):
            for p in self.players:
                p.draw_tile(self.tiles.pop(0))

    def record_action(self, action_type, player, tile=None):
        entry = {
            'time': datetime.now().strftime("%H:%M:%S"),
            'player': player.name,
            'player_tiles': player.hand.copy(),  # 保存玩家当前手牌的副本
            'action': action_type,
            'tile': self.get_tile_name(tile) if tile else None
        }
        self.log.append(entry)

    def get_tile_name(self, tile):
        if tile[-1] in ['m', 't', 'p']:
            return f"{tile[:-1]}{'万' if tile[-1] == 'm' else '条' if tile[-1] == 't' else '筒'}"
        return {'e':'东','s':'南','w':'西','n':'北','z':'中','f':'发','b':'白'}.get(tile, tile)

    def check_win(self, hand, player=None):
        def is_meld(tiles):
            if len(tiles) < 3: return False
            if tiles[0] == tiles[1] == tiles[2]: return True
            if all(tile[-1] in ['m', 't', 'p'] for tile in tiles[:3]):
                nums = [int(t[:-1]) for t in tiles[:3]]
                if nums == [nums[0], nums[0]+1, nums[0]+2]:
                    return True
            return False

        def backtrack(tiles, melds, pair, needed_melds):
            if not tiles:
                return len(melds) == needed_melds and pair is not None
            
            for i in range(len(tiles)):
                if not pair and i+1 < len(tiles) and tiles[i] == tiles[i+1]:
                    if backtrack(tiles[:i]+tiles[i+2:], melds, tiles[i], needed_melds):
                        return True
                if i+2 < len(tiles) and is_meld(tiles[i:i+3]):
                    if backtrack(tiles[:i]+tiles[i+3:], melds+[tiles[i:i+3]], pair, needed_melds):
                        return True
            return False

        def qidui(tiles):
            # 检查是否为七对子
            from collections import Counter
            count = Counter(tiles)
            # 必须恰好有7对牌，每对牌数量必须是2
            if len(count) != 7:
                return False
            for value in count.values():
                if value != 2:
                    return False
            return True

        # 获取玩家已亮出的面子数量
        existing_melds_count = 0
        if player is not None:
            existing_melds_count = len(player.melds)
        else:
            # 如果没有提供player参数，尝试从self获取melds
            if hasattr(self, 'melds'):
                existing_melds_count = len(self.melds)
        
        # 计算还需要的面子数量
        needed_melds = 4 - existing_melds_count
        
        sorted_tiles = sort_hand(hand.copy())
        
        # 如果已亮出的面子数量加上手牌数量不足以凑成4个面子和1对雀头，则不可能和牌
        min_tiles_needed = needed_melds * 3 + 2
        if len(sorted_tiles) < min_tiles_needed:
            return False
        
        # 检查是否为七对子或者普通胡牌
        # 七对子只有在没有亮出面子的情况下才可能成立
        if existing_melds_count == 0 and qidui(sorted_tiles):
            return True
        
        # 普通胡牌，需要考虑已亮出的面子数量
        return backtrack(sorted_tiles, [], None, needed_melds)
    
    def handle_player_action(self, player, discarded_tile=None, discarder_idx=None, current_idx=None):
        """处理玩家对其他玩家打出的牌的响应"""
        if player.is_computer:
            # AI决策
            try:
                from ai_strategy import AdvancedAI
                
                game_state = {
                    'can_hu': self.check_win(player.hand + [discarded_tile], player),
                    'can_gang': player.can_gang(discarded_tile),
                    'can_peng': player.can_peng(discarded_tile),
                    'can_chi': len(player.can_chi(discarded_tile, discarder_idx, current_idx)) > 0,
                    'gang_tile': discarded_tile,
                    'peng_tile': discarded_tile,
                    'chi_options': player.can_chi(discarded_tile)
                }
                
                action, tile = AdvancedAI.decide_action(player, game_state)
                
                if action == 'hu' and game_state['can_hu']:
                    self.winner = player
                    print(f"{player.name} 和牌！")
                    self.record_action('和牌', player, discarded_tile)
                    return True
                
                elif action == 'gang' and game_state['can_gang']:
                    player.perform_gang(discarded_tile)
                    print(f"{player.name} 杠了 {self.get_tile_name(discarded_tile)}")
                    self.record_action('杠', player, discarded_tile)
                    # 杠后摸牌
                    if self.tiles:
                        new_tile = self.tiles.pop(0)
                        player.draw_tile(new_tile)
                        print(f"{player.name} 摸了一张牌")
                        self.record_action('摸牌', player, new_tile)
                        # AI自动打出一张牌
                        discard_tile = player.auto_discard()
                        print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                        self.record_action('弃牌', player, discard_tile)
                    return True
                
                elif action == 'peng' and game_state['can_peng']:
                    player.perform_peng(discarded_tile)
                    print(f"{player.name} 碰了 {self.get_tile_name(discarded_tile)}")
                    self.record_action('碰', player, discarded_tile)
                    # AI自动打出一张牌
                    discard_tile = player.auto_discard()
                    print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                    self.record_action('弃牌', player, discard_tile)
                    return True
                
                elif action == 'chi' and game_state['can_chi']:
                    chi_options = player.can_chi(discarded_tile, discarder_idx, current_idx)
                    option = chi_options[0]  # 选择第一个吃牌选项
                    player.perform_chi(discarded_tile, option)
                    print(f"{player.name} 吃了 {self.get_tile_name(discarded_tile)}")
                    self.record_action('吃', player, discarded_tile)
                    # AI自动打出一张牌
                    discard_tile = player.auto_discard()
                    print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                    self.record_action('弃牌', player, discard_tile)
                    return True
            
            except ImportError:
                # 如果高级AI模块不可用，使用简单策略
                # 简单策略：只检查和牌
                if self.check_win(player.hand + [discarded_tile], player):
                    self.winner = player
                    print(f"{player.name} 和牌！")
                    self.record_action('和牌', player, discarded_tile)
                    return True
        
        else:  # 人类玩家
            # 检查是否可以和牌
            can_hu = self.check_win(player.hand + [discarded_tile], player)
            can_gang = player.can_gang(discarded_tile)
            can_peng = player.can_peng(discarded_tile)
            can_chi = len(player.can_chi(discarded_tile, discarder_idx, current_idx)) > 0
            
            if not (can_hu or can_gang or can_peng or can_chi):
                return False
            
            # 显示当前手牌
            print(f"\n{player.name}的当前手牌：")
            display_hand(player.hand, "你的")
            
            # 显示可选操作
            # 显示可选操作
            print(f"\n{player.name}，你可以对 {self.get_tile_name(discarded_tile)} 进行以下操作：")
            options = []
            option_index = 1
            
            if can_hu:
                options.append("和牌")
                print(f"{option_index}. 和牌")
                option_index += 1
            
            if can_gang:
                options.append("杠")
                print(f"{option_index}. 杠")
                option_index += 1
            
            if can_peng:
                options.append("碰")
                print(f"{option_index}. 碰")
                option_index += 1
            
            if can_chi:
                options.append("吃")
                print(f"{option_index}. 吃")
                option_index += 1
            
            options.append("跳过")
            print(f"{option_index}. 跳过")
            
            while True:
                try:
                    choice = int(input("请选择操作（输入数字）: "))
                    if 1 <= choice <= len(options):
                        action = options[choice-1]
                        break
                    else:
                        print("无效的选择，请重新输入！")
                except ValueError:
                    print("请输入有效的数字！")
            
            if action == "和牌":
                self.winner = player
                print(f"{player.name} 和牌！")
                self.record_action('和牌', player, discarded_tile)
                return True
            
            elif action == "杠":
                player.perform_gang(discarded_tile)
                print(f"{player.name} 杠了 {self.get_tile_name(discarded_tile)}")
                self.record_action('杠', player, discarded_tile)
                # 杠后摸牌
                if self.tiles:
                    new_tile = self.tiles.pop(0)
                    player.draw_tile(new_tile)
                    print(f"{player.name} 摸了一张牌: {self.get_tile_name(new_tile)}")
                    self.record_action('摸牌', player, new_tile)
                    
                    # 显示手牌
                    display_hand(player.hand, "你的")
                    # 要求玩家打出一张牌
                    while True:
                        discard = input("请选择要打出的牌（输入牌代号）: ").strip()
                        if discard in player.hand:
                            break
                        print("无效的牌，请重新输入！")
                    discard_tile = player.discard_tile(discard)
                    print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                    self.record_action('手动弃牌', player, discard_tile)
                return True
            
            elif action == "碰":
                player.perform_peng(discarded_tile)
                print(f"{player.name} 碰了 {self.get_tile_name(discarded_tile)}")
                self.record_action('碰', player, discarded_tile)
                
                # 显示手牌
                display_hand(player.hand, "你的")
                # 要求玩家打出一张牌
                while True:
                    discard = input("请选择要打出的牌（输入牌代号）: ").strip()
                    if discard in player.hand:
                        break
                    print("无效的牌，请重新输入！")
                discard_tile = player.discard_tile(discard)
                print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                self.record_action('手动弃牌', player, discard_tile)
                return True
            
            elif action == "吃":
                chi_options = player.can_chi(discarded_tile, discarder_idx, current_idx)
                if not chi_options:  # 检查chi_options是否为空
                    print("没有可用的吃牌选项！")
                    return False
                    
                if len(chi_options) > 1:
                    print("\n请选择吃牌组合：")
                    for i, option in enumerate(chi_options):
                        option_str = ' '.join([self.get_tile_name(t) for t in option])
                        print(f"{i+1}. {option_str}")
                    
                    while True:
                        try:
                            chi_choice = int(input("请选择吃牌组合（输入数字）: "))
                            if 1 <= chi_choice <= len(chi_options):
                                break
                            else:
                                print("无效的选择，请重新输入！")
                        except ValueError:
                            print("请输入有效的数字！")
                    
                    option = chi_options[chi_choice-1]
                else:
                    option = chi_options[0]
                
                player.perform_chi(discarded_tile, option)
                print(f"{player.name} 吃了 {self.get_tile_name(discarded_tile)}")
                self.record_action('吃', player, discarded_tile)
                
                # 显示手牌
                display_hand(player.hand, "你的")
                # 要求玩家打出一张牌
                while True:
                    discard = input("请选择要打出的牌（输入牌代号）: ").strip()
                    if discard in player.hand:
                        break
                    print("无效的牌，请重新输入！")
                discard_tile = player.discard_tile(discard)
                print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                self.record_action('手动弃牌', player, discard_tile)
                return True
        
        return False

    # 显示所有玩家的丢弃牌
    def display_discards(self):
        print("===公共信息： ===")
        for p in self.players:
            discard_str = ""
            for tile in p.discards:
                discard_str += f"{self.get_tile_name(tile)} "
            print(f"{p.name} 丢弃手牌：{discard_str}")
        print()
        
        # 显示所有玩家的面子
        for p in self.players:
            if p.melds:
                print(f"{p.name}的面子：", end="")
                meld_strs = []
                for meld_type, tiles in p.melds:
                    # 根据面子类型使用不同的显示格式
                    if meld_type == 'chi':
                        meld_str = '吃: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                    elif meld_type == 'peng':
                        meld_str = '碰: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                    elif meld_type == 'gang':
                        meld_str = '杠: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                    else:
                        meld_str = f"{meld_type}: " + ' '.join([self.get_tile_name(t) for t in tiles])
                    meld_strs.append(meld_str)
                print("; ".join(meld_strs))
            else:
                print(f"{p.name}的面子：")
        
        print(f"\n牌山剩余: {len(self.tiles)}张牌\n")
    
    def play_round(self):
        player = self.players[self.current_player]
        
        # 检查是否可以自摸杠
        if player.is_computer:
            self_gang_tiles = player.can_self_gang()
            if self_gang_tiles:
                # AI简单策略：有80%概率选择自摸杠
                if random.random() < 0.8:
                    gang_tile = self_gang_tiles[0]
                    # 检查是否为加杠
                    is_add_gang = False
                    for meld_type, tiles in player.melds:
                        if meld_type == 'peng' and tiles[0] == gang_tile:
                            is_add_gang = True
                            break
                    
                    player.perform_gang(gang_tile, is_self_gang=True, is_add_gang=is_add_gang)
                    gang_type = '加杠' if is_add_gang else '暗杠'
                    print(f"{player.name} {gang_type}了 {self.get_tile_name(gang_tile)}")
                    self.record_action(gang_type, player, gang_tile)
                    # 杠后摸牌
                    if self.tiles:
                        new_tile = self.tiles.pop(0)
                        player.draw_tile(new_tile)
                        print(f"{player.name} 摸了一张牌")
                        self.record_action('摸牌', player, new_tile)
                        # AI自动打出一张牌
                        discard_tile = player.auto_discard()
                        print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                        self.record_action('弃牌', player, discard_tile)
        else:  # 人类玩家
            self_gang_tiles = player.can_self_gang()
            if self_gang_tiles:
                print("\n你可以进行以下杠牌操作：")
                gang_options = []
                for tile in self_gang_tiles:
                    # 检查是否为加杠
                    is_add_gang = False
                    for meld_type, tiles in player.melds:
                        if meld_type == 'peng' and tiles[0] == tile:
                            is_add_gang = True
                            break
                    gang_type = '加杠' if is_add_gang else '暗杠'
                    print(f"{len(gang_options)+1}. {gang_type} {self.get_tile_name(tile)}")
                    gang_options.append((tile, is_add_gang))
                print(f"{len(gang_options)+1}. 不杠")
                
                while True:
                    try:
                        choice = int(input("请选择（输入数字）: "))
                        if 1 <= choice <= len(gang_options)+1:
                            break
                        else:
                            print("无效的选择，请重新输入！")
                    except ValueError:
                        print("请输入有效的数字！")
                
                if choice <= len(gang_options):
                    gang_tile, is_add_gang = gang_options[choice-1]
                    player.perform_gang(gang_tile, is_self_gang=True, is_add_gang=is_add_gang)
                    gang_type = '加杠' if is_add_gang else '暗杠'
                    print(f"{player.name} {gang_type}了 {self.get_tile_name(gang_tile)}")
                    self.record_action(gang_type, player, gang_tile)
                    # 杠后摸牌
                    if self.tiles:
                        new_tile = self.tiles.pop(0)
                        player.draw_tile(new_tile)
                        print(f"{player.name} 摸了一张牌: {self.get_tile_name(new_tile)}")
                        self.record_action('摸牌', player, new_tile)
                        
                        # 显示手牌
                        display_hand(player.hand, "你的")
                        # 要求玩家打出一张牌
                        while True:
                            discard = input("请选择要打出的牌（输入牌代号）: ").strip()
                            if discard in player.hand:
                                break
                            print("无效的牌，请重新输入！")
                        discard_tile = player.discard_tile(discard)
                        print(f"{player.name} 打出了: {self.get_tile_name(discard_tile)}")
                        self.record_action('手动弃牌', player, discard_tile)
        
        # 摸牌
        if not self.tiles:
            print("牌山已空，流局！")
            return False
        
        new_tile = self.tiles.pop(0)
        player.draw_tile(new_tile)
        self.record_action('摸牌', player, new_tile)
        
        if not player.is_computer:
            print(f"\n=== {player.name}的回合 ===")
            # 显示公共信息
            self.display_discards()
            
            print(f" ===你的信息： ===")
            print(f"你摸到了: {self.get_tile_name(new_tile)}")
            display_hand(player.hand, "你的")
            
            # 显示玩家的面子
            if player.melds:
                print("\n你的面子：", end="")
                meld_strs = []
                for meld_type, tiles in player.melds:
                    # 根据面子类型使用不同的显示格式
                    if meld_type == 'chi':
                        meld_str = '吃: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                    elif meld_type == 'peng':
                        meld_str = '碰: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                    elif meld_type == 'gang':
                        meld_str = '杠: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                    else:
                        meld_str = f"{meld_type}: " + ' '.join([self.get_tile_name(t) for t in tiles])
                    meld_strs.append(meld_str)
                print("; ".join(meld_strs))
        else:
            print(f"\n=== {player.name}的回合 ===")
            # 显示公共信息
            self.display_discards()
            
            print(f" ===你的信息： ===")
            if self.show_ai_cards:
                print(f"你摸到了: {self.get_tile_name(new_tile)}")
                display_hand(player.hand, "你的")
                if player.melds:
                    print("\n你的面子：", end="")
                    meld_strs = []
                    for meld_type, tiles in player.melds:
                        # 根据面子类型使用不同的显示格式
                        if meld_type == 'chi':
                            meld_str = '吃: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                        elif meld_type == 'peng':
                            meld_str = '碰: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                        elif meld_type == 'gang':
                            meld_str = '杠: ' + ' '.join([self.get_tile_name(t) for t in tiles])
                        else:
                            meld_str = f"{meld_type}: " + ' '.join([self.get_tile_name(t) for t in tiles])
                        meld_strs.append(meld_str)
                    print("; ".join(meld_strs))
            else:
                print("你摸到了: *")
                print("你的手牌：")
                print("万: *")
                print("条: *")
                print("筒: *")
                print("字牌: *")
                print("\n你的面子：*")

        # 检查自摸和牌
        if self.check_win(player.hand, player):
            if player.is_computer:
                # AI玩家自动胡牌
                self.winner = player
                print(f"{player.name} 自摸和牌！")
                self.record_action('自摸和牌', player)
                return True
            else:
                # 人类玩家选择是否胡牌
                print("\n恭喜！你可以自摸和牌！")
                while True:
                    choice = input("是否胡牌？(y/n): ").strip().lower()
                    if choice in ['y', 'n']:
                        break
                    print("无效的输入，请输入y或n")
                
                if choice == 'y':
                    self.winner = player
                    print(f"{player.name} 自摸和牌！")
                    self.record_action('自摸和牌', player)
                    return True
                else:
                    print(f"{player.name} 选择不胡牌，继续游戏")
                    self.record_action('放弃自摸', player)

        # 打牌
        if player.is_computer:
            discarded = player.auto_discard()
            action_type = '弃牌'
        else:
            while True:
                discarded = input("请选择要打出的牌（输入牌代号）: ").strip()
                if discarded in player.hand:
                    break
                print("无效的牌，请重新输入！")
            discarded = player.discard_tile(discarded)
            action_type = '手动弃牌'

        self.record_action(action_type, player, discarded)
        print(f"{player.name} 打出了: {self.get_tile_name(discarded)}")
        
        # 记录最后打出的牌和打牌者
        self.last_discarded = discarded
        self.last_discarder = self.current_player
        
        # 检查其他玩家是否可以对打出的牌进行操作
        for i in range(1, len(self.players)):
            next_player_idx = (self.current_player + i) % len(self.players)
            next_player = self.players[next_player_idx]
            
            if self.handle_player_action(next_player, discarded, self.current_player, next_player_idx):
                # 如果有玩家进行了操作，更新当前玩家为该玩家的下家
                self.current_player = (next_player_idx + 1) % len(self.players)
                return False
        
        # 如果没有玩家进行操作，轮到下一位玩家
        self.current_player = (self.current_player + 1) % len(self.players)
        return False

    def save_log(self):
        log_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "log\\poker_game_log_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
        filepath = os.path.join(log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=== 麻将牌谱 ===\n")
            round_num = 1
            current_round = 1
            for i, entry in enumerate(self.log):
                # 每四个玩家操作为一轮（假设4个玩家）
                if i > 0 and i % len(self.players) == 0:
                    current_round += 1
                
                # 获取玩家手牌的字符串表示
                hand_str = ""
                if 'player_tiles' in entry and entry['player_tiles']:
                    hand_tiles = entry['player_tiles'].copy()
                    hand_tiles = sort_hand(hand_tiles)
                    hand_str = "手牌: "
                    for tile in hand_tiles:
                        if tile[-1] in ['m', 't', 'p']:
                            hand_str += f"{tile[:-1]}{'万' if tile[-1] == 'm' else '条' if tile[-1] == 't' else '筒'} "
                        else:
                            hand_str += f"{'东' if tile == 'e' else '南' if tile == 's' else '西' if tile == 'w' else '北' if tile == 'n' else '中' if tile == 'z' else '发' if tile == 'f' else '白'} "
                
                # 构建新的日志行
                line = f"[第{current_round}轮] {entry['player']} {entry['action']}"
                if entry['tile']:
                    line += f": {entry['tile']}"
                
                # 添加手牌信息（如果有）
                if hand_str:
                    line += f" ({hand_str.strip()})"
                
                f.write(line + "\n")
            
            if self.winner:
                f.write(f"\n游戏结束！胜利者：{self.winner.name}")
            else:
                f.write("\n游戏结束！流局")
        print(f"牌谱已保存至：{filepath}")

    def play(self):
        print("游戏开始！")
        try:
            while self.tiles and not self.winner:
                if self.play_round():
                    break
                # 每轮结束后显示剩余牌数
                print(f"\n牌山剩余: {len(self.tiles)}张牌")
        finally:
            self.save_log()
        if self.winner:
            print(f"\n恭喜 {self.winner.name} 胡牌！")
        else:
            print("\n牌山已空，流局！")

if __name__ == "__main__":
    game = MahjongGame(players=1)
    game.play()