from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
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
        self.draw_tile_needed = True  # 是否需要摸牌
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建游戏区域
        game_area = QWidget()
        game_layout = QGridLayout(game_area)
        game_layout.setSpacing(10)
        
        # 创建四个方向的玩家区域
        # 上方玩家（电脑2）
        self.top_player = QWidget()
        top_layout = QVBoxLayout(self.top_player)
        top_layout.setSpacing(5)
        
        self.top_name = QLabel('电脑2')
        self.top_name.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.top_name)
        
        self.top_tiles = QLabel(f'手牌: {len(self.game.players[2].hand)}张')
        self.top_tiles.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.top_tiles)
        
        # 上方玩家面子区域
        self.top_melds = QWidget()
        self.top_melds_layout = QHBoxLayout(self.top_melds)
        self.top_melds_layout.setSpacing(2)
        top_layout.addWidget(self.top_melds)
        
        # 上方玩家出牌区
        self.top_discard = QWidget()
        self.top_discard_layout = QHBoxLayout(self.top_discard)
        self.top_discard_layout.setSpacing(2)
        top_layout.addWidget(self.top_discard)
        
        # 左方玩家（电脑1）
        self.left_player = QWidget()
        left_layout = QVBoxLayout(self.left_player)
        left_layout.setSpacing(5)
        
        self.left_name = QLabel('电脑1')
        self.left_name.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.left_name)
        
        self.left_tiles = QLabel(f'手牌: {len(self.game.players[1].hand)}张')
        self.left_tiles.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.left_tiles)
        
        # 左方玩家面子区域
        self.left_melds = QWidget()
        self.left_melds_layout = QVBoxLayout(self.left_melds)
        self.left_melds_layout.setSpacing(2)
        left_layout.addWidget(self.left_melds)
        
        # 左方玩家出牌区
        self.left_discard = QWidget()
        self.left_discard_layout = QVBoxLayout(self.left_discard)
        self.left_discard_layout.setSpacing(2)
        left_layout.addWidget(self.left_discard)
        
        # 右方玩家（电脑3）
        self.right_player = QWidget()
        right_layout = QVBoxLayout(self.right_player)
        right_layout.setSpacing(5)
        
        self.right_name = QLabel('电脑3')
        self.right_name.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.right_name)
        
        self.right_tiles = QLabel(f'手牌: {len(self.game.players[3].hand)}张')
        self.right_tiles.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.right_tiles)
        
        # 右方玩家面子区域
        self.right_melds = QWidget()
        self.right_melds_layout = QVBoxLayout(self.right_melds)
        self.right_melds_layout.setSpacing(2)
        right_layout.addWidget(self.right_melds)
        
        # 右方玩家出牌区
        self.right_discard = QWidget()
        self.right_discard_layout = QVBoxLayout(self.right_discard)
        self.right_discard_layout.setSpacing(2)
        right_layout.addWidget(self.right_discard)
        
        # 中央区域
        self.center_area = QWidget()
        center_layout = QVBoxLayout(self.center_area)
        
        # 牌山信息
        self.tiles_remaining = QLabel(f'剩余牌数：{len(self.game.tiles)}张')
        self.tiles_remaining.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.tiles_remaining)
        
        # 当前玩家指示
        self.current_player_indicator = QLabel('当前回合：玩家')
        self.current_player_indicator.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.current_player_indicator)
        
        # 中央弃牌区域
        self.center_discard = QWidget()
        self.center_discard_layout = QGridLayout(self.center_discard)
        self.center_discard_layout.setSpacing(2)
        center_layout.addWidget(self.center_discard)
        
        # 操作按钮区域
        action_area = QWidget()
        action_layout = QHBoxLayout(action_area)
        
        # 添加摸牌按钮
        self.draw_btn = QPushButton('摸牌')
        self.draw_btn.clicked.connect(self.on_draw_click)
        action_layout.addWidget(self.draw_btn)
        
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
        
        # 下方玩家（玩家）
        self.bottom_player = QWidget()
        bottom_layout = QVBoxLayout(self.bottom_player)
        bottom_layout.setSpacing(5)
        
        # 玩家信息
        self.player_info = QLabel('玩家')
        self.player_info.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.player_info)
        
        # 玩家面子区域
        self.bottom_melds = QWidget()
        self.bottom_melds_layout = QHBoxLayout(self.bottom_melds)
        self.bottom_melds_layout.setSpacing(2)
        bottom_layout.addWidget(self.bottom_melds)
        
        # 玩家出牌区
        self.bottom_discard = QWidget()
        self.bottom_discard_layout = QHBoxLayout(self.bottom_discard)
        self.bottom_discard_layout.setSpacing(2)
        bottom_layout.addWidget(self.bottom_discard)
        
        # 玩家手牌
        self.hand_widget = QWidget()
        self.hand_layout = QHBoxLayout(self.hand_widget)
        self.hand_layout.setSpacing(2)
        bottom_layout.addWidget(self.hand_widget)
        
        # 将所有区域添加到游戏布局
        game_layout.addWidget(self.top_player, 0, 1)
        game_layout.addWidget(self.left_player, 1, 0)
        game_layout.addWidget(self.center_area, 1, 1)
        game_layout.addWidget(self.right_player, 1, 2)
        game_layout.addWidget(self.bottom_player, 2, 1)
        
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
        
        # 更新手牌显示
        self.update_hand_display()
        self.update_all_discard_areas()
        self.update_all_meld_areas()
        
        # 开始游戏
        self.start_game()
    
    def get_tile_display(self, tile):
        """将麻将牌代码转换为显示文本"""
        if tile[-1] in ['m', 't', 'p']:
            suit = tile[-1]
            num = tile[:-1]
            suit_map = {'m': '万', 't': '条', 'p': '筒'}
            return f"{num}{suit_map[suit]}"
        else:
            zi_map = {'e': '东', 's': '南', 'w': '西', 'n': '北', 'z': '中', 'f': '发', 'b': '白'}
            return zi_map.get(tile, tile)

    def update_current_player_indicator(self):
        """更新当前玩家指示器"""
        player_names = ['玩家', '电脑1', '电脑2', '电脑3']
        self.current_player_indicator.setText(f'当前回合：{player_names[self.current_player]}')
        
        # 如果是玩家回合，启用摸牌按钮
        self.draw_btn.setEnabled(self.current_player == 0 and self.draw_tile_needed)
    
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
    
    def update_all_discard_areas(self):
        # 清除并更新所有玩家的出牌区域
        self.update_player_discard_area(0, self.bottom_discard_layout, True)
        self.update_player_discard_area(1, self.left_discard_layout, False)
        self.update_player_discard_area(2, self.top_discard_layout, True)
        self.update_player_discard_area(3, self.right_discard_layout, False)
        
        # 更新中央弃牌区域
        self.update_center_discard_area()
    
    def update_center_discard_area(self):
        """更新中央弃牌区域"""
        # 清除现有弃牌区域
        while self.center_discard_layout.count():
            item = self.center_discard_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 显示所有玩家的弃牌
        row, col = 0, 0
        max_cols = 8  # 每行最多显示的牌数
        
        # 为每个玩家创建一个标签区域
        player_names = ['玩家', '电脑1', '电脑2', '电脑3']
        for i, player in enumerate(self.game.players):
            # 添加玩家名称标签
            name_label = QLabel(player_names[i])
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); color: white; border-radius: 3px;")
            self.center_discard_layout.addWidget(name_label, row, 0, 1, max_cols)
            row += 1
            
            # 显示玩家的弃牌
            col = 0
            for tile in player.discards:
                tile_btn = QPushButton(self.get_tile_display(tile))
                tile_btn.setFixedSize(30, 45)
                tile_btn.setEnabled(False)
                
                # 如果是最后打出的牌，设置特殊样式
                if tile == self.last_discarded and player == self.game.players[self.last_discard_player]:
                    tile_btn.setStyleSheet("background-color: #FFD700; font-weight: bold;")
                
                self.center_discard_layout.addWidget(tile_btn, row, col)
                col += 1
                if col >= max_cols:  # 换行
                    col = 0
                    row += 1
            
            # 确保每个玩家的弃牌区域之间有空行
            if col > 0:  # 如果当前行有牌，则添加新行
                row += 1
            row += 1  # 额外的空行
    
    def update_all_meld_areas(self):
        # 清除并更新所有玩家的面子区域
        self.update_player_meld_area(0, self.bottom_melds_layout, True)
        self.update_player_meld_area(1, self.left_melds_layout, False)
        self.update_player_meld_area(2, self.top_melds_layout, True)
        self.update_player_meld_area(3, self.right_melds_layout, False)
    
    def update_player_meld_area(self, player_idx, layout, horizontal=True):
        # 清除现有面子区域
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 显示玩家的面子
        melds = self.game.players[player_idx].melds
        for meld_type, tiles in melds:
            # 创建面子容器
            meld_container = QFrame()
            meld_container.setFrameShape(QFrame.Box)
            meld_container.setFrameShadow(QFrame.Raised)
            meld_container.setLineWidth(1)
            
            if horizontal:
                meld_layout = QHBoxLayout(meld_container)
            else:
                meld_layout = QVBoxLayout(meld_container)
            meld_layout.setSpacing(1)
            meld_layout.setContentsMargins(2, 2, 2, 2)
            
            # 添加面子中的每张牌
            for tile in tiles:
                tile_btn = QPushButton(self.get_tile_display(tile))
                if horizontal:
                    tile_btn.setFixedSize(30, 45)
                else:
                    tile_btn.setFixedSize(30, 45)
                tile_btn.setEnabled(False)
                meld_layout.addWidget(tile_btn)
            
            layout.addWidget(meld_container)
    
    def update_player_discard_area(self, player_idx, layout, horizontal=True):
        # 清除现有出牌区域
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 显示玩家的出牌
        discards = self.game.players[player_idx].discards
        for tile in discards:
            tile_btn = QPushButton(self.get_tile_display(tile))
            if horizontal:
                tile_btn.setFixedSize(30, 45)
            else:
                tile_btn.setFixedSize(30, 45)
                tile_btn.setStyleSheet(tile_btn.styleSheet() + "text-align: center;")
            tile_btn.setEnabled(False)
            layout.addWidget(tile_btn)
    
    def auto_draw_for_player(self):
        """为玩家自动摸牌"""
        if self.current_player != 0 or not self.draw_tile_needed or self.waiting_action:
            return  # 不是玩家的回合或不需要摸牌或正在等待操作
        
        # 从牌山摸一张牌
        if len(self.game.tiles) > 0:
            new_tile = self.game.tiles.pop(0)
            self.game.players[0].draw_tile(new_tile)
            self.draw_tile_needed = False  # 已经摸过牌
            
            # 更新界面
            self.update_hand_display()
            self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
            
            # 检查是否可以自摸和牌
            if self.game.check_win(self.game.players[0].hand, self.game.players[0]):
                # 提示玩家可以自摸
                self.current_player_indicator.setText('可以自摸和牌！')
                self.hu_btn.setEnabled(True)
                self.pass_btn.setEnabled(True)
                self.waiting_action = 'self_hu'
            
            # 检查是否可以自摸杠
            gang_tiles = self.game.players[0].can_self_gang()
            if gang_tiles:
                # 提示玩家可以杠
                self.current_player_indicator.setText('可以杠牌！')
                self.gang_btn.setEnabled(True)
                self.pass_btn.setEnabled(True)
                self.waiting_action = 'self_gang'
        else:
            # 牌山已空，游戏结束
            self.tiles_remaining.setText('牌山已空，游戏结束')
    
    def on_tile_click(self, tile):
        if self.current_player != 0 or self.waiting_action:
            return  # 不是玩家的回合或正在等待其他操作
        
        if self.draw_tile_needed:
            # 如果需要摸牌，先自动摸牌
            self.auto_draw_for_player()
            return
        
        if self.selected_tile == tile:
            # 再次点击同一张牌表示打出
            self.game.players[0].discard_tile(tile)
            self.selected_tile = None
            self.update_hand_display()
            self.last_discarded = tile
            self.last_discard_player = 0
            
            # 更新中央弃牌区域和玩家弃牌区域
            self.update_all_discard_areas()
            
            # 轮到下一个玩家
            self.current_player = 1  # 轮到下一个玩家
            self.draw_tile_needed = True  # 下一回合需要摸牌
            self.draw_btn.setEnabled(False)  # 禁用摸牌按钮
            self.update_current_player_indicator()
        else:
            # 选中牌
            self.selected_tile = tile
    
    def on_draw_click(self):
        # 直接调用自动摸牌函数
        self.auto_draw_for_player()
    
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
            self.update_all_discard_areas()
            self.update_all_meld_areas()
            
            # 重置状态
            self.waiting_action = None
            self.last_discarded = None
            self.last_discard_player = None
            self.current_player = 0
            self.draw_tile_needed = False  # 吃牌后不需要摸牌
            
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
            self.update_all_discard_areas()
            self.update_all_meld_areas()
            
            # 重置状态
            self.waiting_action = None
            self.last_discarded = None
            self.last_discard_player = None
            self.current_player = 0
            self.draw_tile_needed = False  # 碰牌后不需要摸牌
            
            # 禁用所有操作按钮
            for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
                btn.setEnabled(False)

    def on_gang_click(self):
        if not self.waiting_action:
            return
        
        player = self.game.players[0]
        
        # 处理自摸杠
        if self.waiting_action == 'self_gang':
            gang_tiles = player.can_self_gang()
            if gang_tiles:
                # 执行杠牌操作
                player.perform_gang(gang_tiles[0], is_self_gang=True)
                
                # 更新界面
                self.update_hand_display()
                self.update_all_meld_areas()
                
                # 杠后需要从牌山摸一张牌
                if len(self.game.tiles) > 0:
                    new_tile = self.game.tiles.pop(0)
                    player.draw_tile(new_tile)
                    
                    # 更新界面
                    self.update_hand_display()
                    self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
                
                # 重置状态
                self.waiting_action = None
                self.draw_tile_needed = False  # 杠牌后已经摸过牌
        # 处理明杠
        elif self.last_discarded and player.can_gang(self.last_discarded):
            # 执行杠牌操作
            player.perform_gang(self.last_discarded)
            
            # 更新界面
            self.update_hand_display()
            self.update_all_discard_areas()
            self.update_all_meld_areas()
            
            # 杠后需要从牌山摸一张牌
            if len(self.game.tiles) > 0:
                new_tile = self.game.tiles.pop(0)
                player.draw_tile(new_tile)
                
                # 更新界面
                self.update_hand_display()
                self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
            
            # 重置状态
            self.waiting_action = None
            self.last_discarded = None
            self.last_discard_player = None
            self.current_player = 0
            self.draw_tile_needed = False  # 杠牌后已经摸过牌
        
        # 禁用所有操作按钮
        for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
            btn.setEnabled(False)

    def on_hu_click(self):
        if not self.waiting_action:
            return
        
        player = self.game.players[0]
        
        # 处理自摸和牌
        if self.waiting_action == 'self_hu':
            if self.game.check_win(player.hand, player):
                # 设置赢家
                self.game.winner = player
                
                # 更新界面
                self.current_player_indicator.setText('游戏结束，玩家自摸获胜！')
                
                # 禁用所有按钮
                for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn, self.draw_btn]:
                    btn.setEnabled(False)
                
                # 停止AI定时器
                self.ai_timer.stop()
        # 处理和牌
        elif self.last_discarded and self.game.check_win(player.hand + [self.last_discarded], player):
            # 设置赢家
            self.game.winner = player
            
            # 更新界面
            self.current_player_indicator.setText('游戏结束，玩家和牌获胜！')
            
            # 禁用所有按钮
            for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn, self.draw_btn]:
                btn.setEnabled(False)
            
            # 停止AI定时器
            self.ai_timer.stop()
        
        # 重置状态
        self.waiting_action = None
        self.last_discarded = None
        self.last_discard_player = None

    def on_pass_click(self):
        if not self.waiting_action:
            return
        
        # 重置状态
        self.waiting_action = None
        
        # 禁用所有操作按钮
        for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn]:
            btn.setEnabled(False)
        
        # 如果是自摸杠或自摸和，继续玩家回合
        if self.waiting_action in ['self_gang', 'self_hu']:
            self.current_player = 0
            self.draw_tile_needed = False
        else:
            # 轮到下一个玩家
            self.current_player = (self.last_discard_player + 1) % 4
            self.draw_tile_needed = True  # 下一回合需要摸牌
        
        # 更新当前玩家指示器
        self.update_current_player_indicator()

    def start_game(self):
        """开始游戏"""
        # 设置初始玩家
        self.current_player = 0
        self.draw_tile_needed = True
        
        # 更新当前玩家指示器
        self.update_current_player_indicator()
        
        # 更新牌山信息
        self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
        
        # 自动为玩家摸牌
        QTimer.singleShot(500, self.auto_draw_for_player)
        
        # 启

    def handle_ai_turn(self):
        """处理AI玩家的回合"""
        # 如果游戏已经结束，不执行任何操作
        if self.game.winner is not None:
            return
        
        # 如果当前是玩家回合或正在等待操作，不执行任何操作
        if self.current_player == 0 or self.waiting_action:
            return
        
        # 获取当前AI玩家
        ai_player = self.game.players[self.current_player]
        
        # 如果需要摸牌
        if self.draw_tile_needed:
            # 从牌山摸一张牌
            if len(self.game.tiles) > 0:
                new_tile = self.game.tiles.pop(0)
                ai_player.draw_tile(new_tile)
                self.draw_tile_needed = False  # 已经摸过牌
                
                # 更新界面
                self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
                
                # 检查是否可以自摸杠
                gang_tiles = ai_player.can_self_gang()
                if gang_tiles:
                    # AI选择第一个可以杠的牌
                    gang_tile = gang_tiles[0]
                    # 执行杠牌操作
                    ai_player.perform_gang(gang_tile, is_self_gang=True)
                    
                    # 更新界面
                    self.update_all_meld_areas()
                    
                    # 杠后需要从牌山摸一张牌
                    if len(self.game.tiles) > 0:
                        new_tile = self.game.tiles.pop(0)
                        ai_player.draw_tile(new_tile)
                        
                        # 更新界面
                        self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
                
                # 检查是否可以自摸和牌
                if self.game.check_win(ai_player.hand, ai_player):
                    # 设置赢家
                    self.game.winner = ai_player
                    
                    # 更新界面
                    self.current_player_indicator.setText(f'游戏结束，{ai_player.name}自摸获胜！')
                    
                    # 禁用所有按钮
                    for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn, self.draw_btn]:
                        btn.setEnabled(False)
                    
                    # 停止AI定时器
                    self.ai_timer.stop()
                    return
            else:
                # 牌山已空，游戏结束
                self.tiles_remaining.setText('牌山已空，游戏结束')
                self.ai_timer.stop()
                return
        
        # AI打出一张牌
        discarded_tile = ai_player.auto_discard()
        
        # 更新界面
        self.update_all_discard_areas()
        
        # 设置最后打出的牌和玩家
        self.last_discarded = discarded_tile
        self.last_discard_player = self.current_player
        
        # 检查其他玩家是否可以吃碰杠和
        for i in range(1, 4):
            next_player_idx = (self.current_player + i) % 4
            next_player = self.game.players[next_player_idx]
            
            # 检查是否可以和牌
            if self.game.check_win(next_player.hand + [discarded_tile], next_player):
                if next_player_idx == 0:  # 如果是玩家可以和牌
                    # 设置等待操作
                    self.waiting_action = 'hu'
                    
                    # 启用和牌按钮
                    self.hu_btn.setEnabled(True)
                    self.pass_btn.setEnabled(True)
                    
                    # 更新当前玩家指示器
                    self.current_player_indicator.setText('可以和牌！')
                    return
                else:  # 如果是AI可以和牌
                    # 设置赢家
                    self.game.winner = next_player
                    
                    # 更新界面
                    self.current_player_indicator.setText(f'游戏结束，{next_player.name}和牌获胜！')
                    
                    # 禁用所有按钮
                    for btn in [self.chi_btn, self.peng_btn, self.gang_btn, self.hu_btn, self.pass_btn, self.draw_btn]:
                        btn.setEnabled(False)
                    
                    # 停止AI定时器
                    self.ai_timer.stop()
                    return
            
            # 检查是否可以杠牌
            if next_player.can_gang(discarded_tile):
                if next_player_idx == 0:  # 如果是玩家可以杠牌
                    # 设置等待操作
                    self.waiting_action = 'gang'
                    
                    # 启用杠牌按钮
                    self.gang_btn.setEnabled(True)
                    self.pass_btn.setEnabled(True)
                    
                    # 更新当前玩家指示器
                    self.current_player_indicator.setText('可以杠牌！')
                    return
                else:  # 如果是AI可以杠牌
                    # 执行杠牌操作
                    next_player.perform_gang(discarded_tile)
                    
                    # 更新界面
                    self.update_all_meld_areas()
                    
                    # 杠后需要从牌山摸一张牌
                    if len(self.game.tiles) > 0:
                        new_tile = self.game.tiles.pop(0)
                        next_player.draw_tile(new_tile)
                        
                        # 更新界面
                        self.tiles_remaining.setText(f'剩余牌数：{len(self.game.tiles)}张')
                    
                    # 设置当前玩家为杠牌的玩家
                    self.current_player = next_player_idx
                    self.draw_tile_needed = False  # 杠牌后已经摸过牌
                    
                    # 更新当前玩家指示器
                    self.update_current_player_indicator()
                    return
            
            # 检查是否可以碰牌
            if next_player.can_peng(discarded_tile):
                if next_player_idx == 0:  # 如果是玩家可以碰牌
                    # 设置等待操作
                    self.waiting_action = 'peng'
                    
                    # 启用碰牌按钮
                    self.peng_btn.setEnabled(True)
                    self.pass_btn.setEnabled(True)
                    
                    # 更新当前玩家指示器
                    self.current_player_indicator.setText('可以碰牌！')
                    return
                else:  # 如果是AI可以碰牌
                    # 执行碰牌操作
                    next_player.perform_peng(discarded_tile)
                    
                    # 更新界面
                    self.update_all_meld_areas()
                    
                    # 设置当前玩家为碰牌的玩家
                    self.current_player = next_player_idx
                    self.draw_tile_needed = False  # 碰牌后不需要摸牌
                    
                    # 更新当前玩家指示器
                    self.update_current_player_indicator()
                    return
            
            # 检查是否可以吃牌（只有下家可以吃）
            if i == 1 and next_player.can_chi(discarded_tile, self.current_player, next_player_idx):
                if next_player_idx == 0:  # 如果是玩家可以吃牌
                    # 设置等待操作
                    self.waiting_action = 'chi'
                    
                    # 启用吃牌按钮
                    self.chi_btn.setEnabled(True)
                    self.pass_btn.setEnabled(True)
                    
                    # 更新当前玩家指示器
                    self.current_player_indicator.setText('可以吃牌！')
                    return
                else:  # 如果是AI可以吃牌
                    # 获取吃牌选项
                    chi_options = next_player.can_chi(discarded_tile, self.current_player, next_player_idx)
                    
                    # 执行吃牌操作
                    next_player.perform_chi(discarded_tile, chi_options[0])
                    
                    # 更新界面
                    self.update_all_meld_areas()
                    
                    # 设置当前玩家为吃牌的玩家
                    self.current_player = next_player_idx
                    self.draw_tile_needed = False  # 吃牌后不需要摸牌
                    
                    # 更新当前玩家指示器
                    self.update_current_player_indicator()
                    return
        
        # 如果没有玩家可以吃碰杠和，轮到下一个玩家
        self.current_player = (self.current_player + 1) % 4
        self.draw_tile_needed = True  # 下一回合需要摸牌
        
        # 更新当前玩家指示器
        self.update_current_player_indicator()

def main():
    app = QApplication(sys.argv)
    window = MahjongUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()