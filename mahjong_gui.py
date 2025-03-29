from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
import sys
from player_class import MahjongGame, Player

class MahjongUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('日本麻将')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建游戏实例
        self.game = MahjongGame(human_players=1, ai_players=3, show_ai_cards=True)
        self.current_player = 0  # 当前玩家索引
        self.selected_tile = None  # 当前选中的牌
        self.waiting_action = None  # 等待的动作（吃/碰/杠/和）
        self.last_discarded = None  # 最后打出的牌
        self.last_discard_player = None  # 最后打出牌的玩家
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建游戏区域
        game_area = QWidget()
        game_layout = QVBoxLayout(game_area)
        
        # 创建对手区域
        opponents_area = QWidget()
        opponents_layout = QHBoxLayout(opponents_area)
        
        # 添加三个AI玩家的信息
        self.opponent_labels = []
        for i in range(1, 4):
            opponent_info = QWidget()
            opponent_layout = QVBoxLayout(opponent_info)
            
            # AI玩家名称
            name_label = QLabel(f'电脑{i}')
            name_label.setAlignment(Qt.AlignCenter)
            opponent_layout.addWidget(name_label)
            
            # AI玩家手牌数量
            tiles_label = QLabel(f'手牌: {len(self.game.players[i].hand)}张')
            tiles_label.setAlignment(Qt.AlignCenter)
            opponent_layout.addWidget(tiles_label)
            
            # 保存标签引用以便更新
            self.opponent_labels.append(tiles_label)
            
            opponents_layout.addWidget(opponent_info)
        
        game_layout.addWidget(opponents_area)
        
        # 创建中央信息区
        center_area = QWidget()
        center_layout = QVBoxLayout(center_area)
        
        # 创建牌山显示区
        self.tiles_remaining = QLabel(f'剩余牌数：{len(self.game.tiles)}张')
        self.tiles_remaining.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.tiles_remaining)
        
        # 创建出牌区域
        self.discard_area = QWidget()
        self.discard_layout = QGridLayout(self.discard_area)
        self.discard_layout.setSpacing(5)
        center_layout.addWidget(self.discard_area)
        
        # 创建操作按钮区域
        action_area = QWidget()
        action_layout = QHBoxLayout(action_area)
        
        # 添加吃碰杠和按钮
        self.chi_btn = QPushButton('吃')
        self.peng_btn = QPushButton('碰')
        self.gang_btn = QPushButton('杠')
        self.hu_btn = QPushButton('和')
        self.pass_btn = QPushButton('过')
        
        # 连接按钮信号
        self.chi_btn.clicked.connect(self.on_chi_click)
        self.peng_btn.clicked.connect(self.on_peng_click)
        self.gang_btn.clicked.connect(self.on_gang_click)
        self.hu_btn.clicked.connect(self.on_hu_click)
        self.pass_btn.clicked.connect(self.on_pass_click)
        
        # 添加按钮到布局
        for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
            action_layout.addWidget(btn)
            btn.setEnabled(False)  # 初始状态下禁用所有按钮
        
        center_layout.addWidget(action_area)
        game_layout.addWidget(center_area)
        
        # 创建玩家手牌区
        player_area = QWidget()
        player_layout = QVBoxLayout(player_area)
        
        # 玩家信息
        self.player_info = QLabel('玩家')
        self.player_info.setAlignment(Qt.AlignCenter)
        player_layout.addWidget(self.player_info)
        
        # 玩家手牌
        self.hand_widget = QWidget()
        self.hand_layout = QHBoxLayout(self.hand_widget)
        self.hand_layout.setSpacing(2)
        
        # 更新手牌显示
        self.update_hand_display()
        
        player_layout.addWidget(self.hand_widget)
        game_layout.addWidget(player_area)
        
        # 添加游戏区域到主布局
        main_layout.addWidget(game_area)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2F4F4F;
            }
            QLabel {
                color: white;
                font-size: 16px;
                background-color: rgba(0, 0, 0, 0.3);
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: white;
                border: 2px solid #4A4A4A;
                border-radius: 5px;
                font-size: 14px;
                min-width: 60px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        
        # 启动AI定时器
        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self.handle_ai_turn)
        self.ai_timer.start(1000)  # 每秒检查一次
        
        # 开始游戏
        self.start_game()
    
    def update_hand_display(self):
        # 清除现有手牌显示
        while self.hand_layout.count():
            item = self.hand_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新的手牌按钮
        for tile in sorted(self.game.players[0].hand):
            tile_btn = QPushButton(self.get_tile_display(tile))
            tile_btn.setFixedSize(40, 60)
            tile_btn.clicked.connect(lambda checked, t=tile: self.on_tile_click(t))
            self.hand_layout.addWidget(tile_btn)
    
    def update_discard_area(self):
        # 清除现有出牌区域
        while self.discard_layout.count():
            item = self.discard_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 显示每个玩家的出牌
        for player_idx in range(4):
            discards = self.game.players[player_idx].discards
            row = player_idx
            for col, tile in enumerate(discards):
                tile_btn = QPushButton(self.get_tile_display(tile))
                tile_btn.setFixedSize(30, 45)
                tile_btn.setEnabled(False)
                self.discard_layout.addWidget(tile_btn, row, col)
    
    def on_tile_click(self, tile):
        if self.current_player != 0 or self.waiting_action:
            return  # 不是玩家的回合或正在等待其他操作
        
        if self.selected_tile == tile:
            # 再次点击同一张牌表示打出
            self.game.players[0].discard_tile(tile)
            self.selected_tile = None
            self.update_hand_display()
            self.update_discard_area()
            self.last_discarded = tile
            self.last_discard_player = 0
            self.current_player = 1  # 轮到下一个玩家
        else:
            # 选中牌
            self.selected_tile = tile
    
    def handle_ai_turn(self):
        if self.current_player == 0 or self.waiting_action:
            return  # 不是AI的回合或正在等待操作
        
        # AI执行打牌
        player = self.game.players[self.current_player]
        discarded_tile = player.auto_discard()
        
        # 更新界面
        self.opponent_labels[self.current_player-1].setText(f'手牌: {len(player.hand)}张')
        self.update_discard_area()
        
        # 设置最后打出的牌信息
        self.last_discarded = discarded_tile
        self.last_discard_player = self.current_player
        
        # 检查其他玩家是否可以吃碰杠和
        self.check_player_actions()
        
        # 如果没有等待操作，轮到下一个玩家
        if not self.waiting_action:
            self.current_player = (self.current_player + 1) % 4
    
    def check_player_actions(self):
        if self.last_discarded is None:
            return
        
        # 检查玩家是否可以吃碰杠和
        player = self.game.players[0]
        can_chi = player.can_chi(self.last_discarded, self.last_discard_player, 0)
        can_peng = player.can_peng(self.last_discarded)
        can_gang = player.can_gang(self.last_discarded)
        
        # 更新按钮状态
        self.chi_btn.setEnabled(bool(can_chi))
        self.peng_btn.setEnabled(can_peng)
        self.gang_btn.setEnabled(can_gang)
        self.pass_btn.setEnabled(True)
        
        if can_chi or can_peng or can_gang:
            self.waiting_action = True
    
    def start_game(self):
        # 初始化游戏状态
        self.current_player = 0
        self.selected_tile = None
        self.waiting_action = None
        self.last_discarded = None
        self.last_discard_player = None
        
        # 更新界面
        self.update_hand_display()
        self.update_discard_area()
        self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
    
    def get_tile_display(self, tile):

        # 转换牌代码为显示字符
        if len(tile) != 2:
            # 处理特殊字牌
            zi_map = {'e':'东', 's':'南', 'w':'西', 'n':'北', 'z':'中', 'f':'发', 'b':'白'}
            return zi_map.get(tile, tile)
        
        tile_type = tile[0]  # 获取牌的数字
        tile_suit = tile[1]  # 获取牌的类型
        
        if tile_suit == 'm':
            return f'{tile_type}万'
        elif tile_suit == 't':
            return f'{tile_type}条'
        elif tile_suit == 'p':
            return f'{tile_type}筒'
        return tile

    def on_chi_click(self):
        if not self.waiting_action or not self.last_discarded:
            return
        
        # 获取吃牌选项
        player = self.game.players[0]
        chi_options = player.can_chi(self.last_discarded, self.last_discard_player, 0)
        
        if chi_options:
            # 执行吃牌操作
            player.perform_chi(self.last_discarded, chi_options[0])
            
            # 更新界面
            self.update_hand_display()
            self.update_discard_area()
            
            # 重置状态
            self.waiting_action = None
            self.last_discarded = None
            self.last_discard_player = None
            self.current_player = 0
            
            # 禁用所有操作按钮
            for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
                btn.setEnabled(False)
    
    def on_peng_click(self):
        if not self.waiting_action or not self.last_discarded:
            return
        
        player = self.game.players[0]
        if player.can_peng(self.last_discarded):
            # 执行碰牌操作
            player.perform_peng(self.last_discarded)
            
            # 更新界面
            self.update_hand_display()
            self.update_discard_area()
            
            # 重置状态
            self.waiting_action = None
            self.last_discarded = None
            self.last_discard_player = None
            self.current_player = 0
            
            # 禁用所有操作按钮
            for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
                btn.setEnabled(False)
    
    def on_gang_click(self):
        if not self.waiting_action or not self.last_discarded:
            return
        
        player = self.game.players[0]
        if player.can_gang(self.last_discarded):
            # 执行杠牌操作
            player.perform_gang(self.last_discarded)
            
            # 更新界面
            self.update_hand_display()
            self.update_discard_area()
            
            # 重置状态
            self.waiting_action = None
            self.last_discarded = None
            self.last_discard_player = None
            self.current_player = 0
            
            # 禁用所有操作按钮
            for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
                btn.setEnabled(False)
    
    def on_hu_click(self):
        # 和牌功能待实现
        pass
    
    def on_pass_click(self):
        if not self.waiting_action:
            return
        
        # 重置状态
        self.waiting_action = None
        
        # 禁用所有操作按钮
        for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
            btn.setEnabled(False)
        
        # 轮到下一个玩家
        self.current_player = (self.last_discard_player + 1) % 4

def main():
    app = QApplication(sys.argv)
    window = MahjongUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()