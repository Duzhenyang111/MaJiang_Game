import random

# 麻将牌型评估
class MahjongEvaluator:
    @staticmethod
    def count_tiles(hand):
        """统计手牌中每种牌的数量"""
        count = {}
        for tile in hand:
            count[tile] = count.get(tile, 0) + 1
        return count
    
    @staticmethod
    def find_pairs(hand_count):
        """找出所有对子"""
        return [tile for tile, count in hand_count.items() if count >= 2]
    
    @staticmethod
    def find_potential_melds(hand, hand_count):
        """找出潜在的面子（顺子或刻子）"""
        potential_melds = []
        
        # 寻找刻子
        for tile, count in hand_count.items():
            if count >= 3:
                potential_melds.append((tile, tile, tile))
        
        # 寻找顺子（仅适用于数牌）
        for tile in hand:
            if tile[-1] in ['m', 't', 'p']:
                suit = tile[-1]
                num = int(tile[:-1])
                
                # 检查是否可以形成顺子
                if num <= 7:  # 确保不会超出9
                    next_tile = f"{num+1}{suit}"
                    next_next_tile = f"{num+2}{suit}"
                    
                    if next_tile in hand and next_next_tile in hand:
                        potential_melds.append((tile, next_tile, next_next_tile))
        
        return potential_melds
    
    @staticmethod
    def calculate_shanten(hand):
        """计算向听数（简化版）
        向听数是达到听牌状态还需要的最少步数
        0表示已经听牌，-1表示已经和牌
        """
        # 这是一个简化版的向听数计算，实际麻将中更复杂
        hand_count = MahjongEvaluator.count_tiles(hand)
        pairs = MahjongEvaluator.find_pairs(hand_count)
        potential_melds = MahjongEvaluator.find_potential_melds(hand, hand_count)
        
        # 简单估算：需要4组面子和1对雀头
        # 每个已有的面子贡献1分，每个对子贡献0.5分
        score = len(potential_melds) + (0.5 * min(1, len(pairs)))  # 最多计算一个对子
        
        # 向听数 = 5(总共需要的组合) - 已有的组合数
        shanten = 5 - score
        
        # 调整为整数
        return max(0, int(shanten))
    
    @staticmethod
    def evaluate_tile_value(tile, hand):
        """评估一张牌的价值"""
        # 复制手牌并移除要评估的牌
        test_hand = hand.copy()
        test_hand.remove(tile)
        
        # 计算移除该牌后的向听数
        shanten_after = MahjongEvaluator.calculate_shanten(test_hand)
        
        # 基础分数：向听数越低越好
        score = 100 - (shanten_after * 20)
        
        # 额外评估
        hand_count = MahjongEvaluator.count_tiles(hand)
        
        # 孤张牌价值低
        if hand_count.get(tile, 0) == 1:
            score -= 10
        
        # 对子和刻子有价值
        if hand_count.get(tile, 0) >= 2:
            score += 15
        
        # 边张（1和9）价值较低
        if tile[-1] in ['m', 't', 'p']:
            num = int(tile[:-1])
            if num == 1 or num == 9:
                score -= 5
        
        # 字牌单张价值低
        if tile in ['e', 's', 'w', 'n', 'z', 'f', 'b'] and hand_count.get(tile, 0) == 1:
            score -= 8
        
        return score

class AdvancedAI:
    @staticmethod
    def select_discard_tile(hand):
        """选择要打出的牌"""
        # 如果手牌为空，返回None
        if not hand:
            return None
        
        # 评估每张牌的价值
        tile_values = {}
        for tile in hand:
            tile_values[tile] = MahjongEvaluator.evaluate_tile_value(tile, hand)
        
        # 选择价值最低的牌打出
        return min(tile_values, key=tile_values.get)
    
    @staticmethod
    def decide_action(player, game_state):
        """决定AI的行动
        
        Args:
            player: 玩家对象
            game_state: 游戏状态信息
            
        Returns:
            action: 行动类型 ('discard', 'chi', 'peng', 'gang', 'hu')
            tile: 相关的牌
        """
        # 默认行动是打牌
        action = 'discard'
        
        # 检查是否可以和牌
        if game_state.get('can_hu', False):
            return 'hu', None
        
        # 检查是否可以杠
        if game_state.get('can_gang', False):
            # 简单策略：有80%概率选择杠
            if random.random() < 0.8:
                return 'gang', game_state.get('gang_tile')
        
        # 检查是否可以碰
        if game_state.get('can_peng', False):
            # 简单策略：有60%概率选择碰
            if random.random() < 0.6:
                return 'peng', game_state.get('peng_tile')
        
        # 检查是否可以吃
        if game_state.get('can_chi', False):
            # 简单策略：有40%概率选择吃
            if random.random() < 0.4:
                chi_options = game_state.get('chi_options', [])
                if chi_options:  # 确保有可用的吃牌选项
                    return 'chi', chi_options[0]  # 选择第一个吃牌选项
                else:
                    return 'pass', None  # 如果没有可用的吃牌选项，则跳过
        
        # 默认打牌
        discard_tile = AdvancedAI.select_discard_tile(player.hand)
        return action, discard_tile