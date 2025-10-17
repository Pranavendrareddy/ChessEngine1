import chess

KILLER_SCORE = 3500
PV_SCORE = 100000

class MoveOrder:
    def __init__(self, killers_store_size: int=2):
        self.killer_moves = {}
        self.killers_store_size = killers_store_size

    def store_killer_move(self, depth, move, board):
        if board.is_capture(move):
            return
        killers = self.killer_moves.setdefault(depth, [])

        if move in killers:
            return
        if len(killers) < self.killers_store_size:
            killers.append(move)
        else:
            #killers_temp = killers[1:-1]
            #killers_temp.append(move)
            #killers = killers_temp
            killers.pop(0)
            killers.append(move)

        self.killer_moves[depth] = killers

    def clear_killer_moves(self):
        self.killer_moves.clear()

    def killer_score(self, move, depth):
        killers = self.killer_moves.get(depth, [])
        if move in killers:
        # newer killer (index -1) gets slightly higher implicit score
            if len(killers) == self.killers_store_size and move == killers[-1]:
                return KILLER_SCORE + 1000
            return KILLER_SCORE
        return 0

    def order_moves(self, board, pv_move, piece_values, depth):
        moves = board.legal_moves
        moves_scores = []

        for move in moves:
            move_score_guess = 0
            move_piece = board.piece_type_at(move.from_square)
            move_capture_piece = board.piece_type_at(move.to_square)

            #principle variation first
            if pv_move is not None and move==pv_move:
                move_score_guess += PV_SCORE
                #print("hi", pv_move)

            #capture high piece with low piece
            if move_capture_piece is not None:
                is_attacking = move.to_square in board.attacks(move.from_square)
                if is_attacking:
                    move_score_guess += 10 * piece_values[move_capture_piece] - piece_values[move_piece]

            #promoting pawn
            if move.promotion is not None:
                move_score_guess += 10 * piece_values[move.promotion]

            #move where piece will be attacked
            if board.is_attacked_by(not board.turn, move.to_square):
                move_score_guess -= piece_values[move_piece]

            #killer move score
            move_score_guess += self.killer_score(move, depth)


            moves_scores.append((move_score_guess, move))

        moves_scores.sort(key=lambda x: x[0], reverse=True)

        #sorted_moves = [x for _,x in sorted(zip(moves_scores, moves), key=lambda x: x[0], reverse = True)]
        #sorted_moves_scores = sorted(moves_scores)

        #return zip(sorted_moves, sorted_moves_scores)
        return [move for score, move in moves_scores]

    def order_quiescence_moves(self, board, piece_values):
        moves = board.legal_moves

        quiescence_moves = []
        for move in moves:
            if board.is_capture(move) or move.promotion is not None:
                quiescence_moves.append(move)


        moves_scores = []
        for move in quiescence_moves:
            move_piece = board.piece_type_at(move.from_square)
            move_capture_piece = board.piece_type_at(move.to_square)

            move_score_guess = 0

            if move_capture_piece is not None:
                move_score_guess = 10 * piece_values[move_capture_piece] - piece_values[move_piece]
            if move.promotion is not None:
                move_score_guess += 10 * piece_values[move.promotion]

            moves_scores.append((move_score_guess, move))

        moves_scores.sort(key=lambda x: x[0], reverse=True)
        return [move for score, move in moves_scores]