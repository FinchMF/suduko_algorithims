

##########################
# S U D O K U  T O O L S #
##########################
import random, math, time
from random import sample

class Sudoku_Core():
    def __init__(self, base):
        self.base = base
        self.side = base*base
        self.row_base = range(self.base)
        self.rows = [g*self.base + row for g in self.shuffle(self.row_base) for row in self.shuffle(self.row_base)]
        self.cols = [g*self.base + col for g in self.shuffle(self.row_base) for col in self.shuffle(self.row_base)]
        self.nums = self.shuffle(range(self.base*self.base+1))
        self.board = [[self.nums[self.baseline_pattern(row, col)] for col in self.cols] for row in self.rows]
        self.square = self.side*self.side
        self.empty_cells = self.square * 3//4
        self.numSize = len(str(self.side))

        self.line0 = self.pretty_line("╔═══╤═══╦═══╗")
        self.line1 = self.pretty_line("║ . │ . ║ . ║")
        self.line2 = self.pretty_line("╟───┼───╫───╢")
        self.line3 = self.pretty_line("╠═══╪═══╬═══╣")
        self.line4 = self.pretty_line("╚═══╧═══╩═══╝")

        self.game = self.gen_game_board()

        self.symbol = ' 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        self.N = [ [""]+[self.symbol[n] for n in row] for row in self.game ]

        
    def baseline_pattern(self, row, col): return (self.base * (row%self.base) + row // self.base+col)%self.side

    def shuffle(self, s): return sample(s,len(s))

    def gen_full_board(self):
        for line in self.board: print(line)
    
    def gen_game_board(self):
        for cell in sample(range(self.square), self.empty_cells):
            self.board[cell//self.side][cell%self.side] = 0

        string_board = []
        for line in self.board:
            string_board.append([" ".join(f'{n or 0 :{self.numSize}}' for n in line)])
        
        game_board = []
        for idx in range(9):
            line = [int(i) for i in string_board[idx][0].split(' ')]
            game_board.append(line)    
        
        return game_board
    
    def pretty_line(self,line): return line[0]+line[5:9].join([line[1:5]*(self.base-1)] * self.base)+line[9:13]

    def pretty_print_board(self):
        print(self.line0)
        for r in range(1, self.side+1):
            print("".join(n+s for n,s in zip(self.N[r-1], self.line1.split("."))))
            print([self.line2, self.line3, self.line4][(r%self.side==0)+(r%self.base==0)])



class Sudoku_Logic:
    def __init__( self, _g=[] ):
        self._input_grid = [] 
        self.grid = [] 
        for i in _g: 
            self._input_grid.append( i[:] )
            self.grid.append( i[:] )

        self.empty_cells = set() 
        self.empty_cells_initial = set() 
        self.current_cell = None 
        self.current_choice = 0 
        self.history = [] 
        self.choices = {} 
        self.nextCellWeights = {} 
        self.nextCellWeights_1 = lambda x: None 
        self.nextCellWeights_2 = lambda x: None 
        self.nextChoiceWeights = {} 
        self.nextChoiceWeights_1 = lambda x: None 
        self.nextChoiceWeights_2 = lambda x: None 

        self.search_space = 1 
        self.iterations = 0 
        self.iterations_backtrack = 0 

        self.digit_heuristic = { 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0 } 
        self.centerWeights = {} 

        # populate centerWeights with Pythagorean theorem
        for id in range( 81 ):
            row = id // 9
            col = id % 9
            self.centerWeights[ id ] = int( round( 100 * math.sqrt( (row-4)**2 + (col-4)**2 ) ) )



    
    def dump( self, _custom_text, _file_object ):
        _custom_text += ", cell: {}, choice: {}, choices: {}, empty: {}, history: {}, grid: {}\n".format(
            self.current_cell, self.current_choice, self.choices, self.empty_cells, self.history, self.grid )
        _file_object.write( _custom_text )

    
    def reset( self ):
        self.grid = []
        for i in self._input_grid:
            self.grid.append( i[:] )

        self.empty_cells = set()
        self.empty_cells_initial = set()
        self.current_cell = None
        self.current_choice = 0
        self.history = []
        self.choices = {}

        self.nextCellWeights = {}
        self.nextCellWeights_1 = lambda x: None
        self.nextCellWeights_2 = lambda x: None
        self.nextChoiceWeights = {}
        self.nextChoiceWeights_1 = lambda x: None
        self.nextChoiceWeights_2 = lambda x: None

        self.search_space = 1
        self.iterations = 0
        self.iterations_backtrack = 0

        self.digit_heuristic = { 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0 }

    def validate( self ):
        # validate all rows
        for x in range(9):
            digit_count = { 0:1, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0 }
            for y in range(9):
                digit_count[ self.grid[ x ][ y ] ] += 1
            for i in digit_count:
                if digit_count[ i ] != 1:
                    return False

        # validate all columns
        for x in range(9):
            digit_count = { 0:1, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0 }
            for y in range(9):
                digit_count[ self.grid[ y ][ x ] ] += 1
            for i in digit_count:
                if digit_count[ i ] != 1:
                    return False

        # validate all 3x3 quadrants
        def validate_quadrant( _grid, from_row, to_row, from_col, to_col ):
            digit_count = { 0:1, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0 }
            for x in range( from_row, to_row + 1 ):
                for y in range( from_col, to_col + 1 ):
                    digit_count[ _grid[ x ][ y ] ] += 1
            for i in digit_count:
                if digit_count[ i ] != 1:
                    return False
            return True

        for x in range( 0, 7, 3 ):
            for y in range( 0, 7, 3 ):
                if not validate_quadrant( self.grid, x, x+2, y, y+2 ):
                    return False
        return True

    def setCell( self, _id, _value ):
        row = _id // 9
        col = _id % 9
        self.grid[ row ][ col ] = _value

    def getCell( self, _id ):
        row = _id // 9
        col = _id % 9
        return self.grid[ row ][ col ]

   
    def getRelatedBlankCells( self, _id ):
        result = set()
        row = _id // 9
        col = _id % 9

        for i in range( 9 ):
            if self.grid[ row ][ i ] == 0: result.add( row * 9 + i )
        for i in range( 9 ):
            if self.grid[ i ][ col ] == 0: result.add( i * 9 + col )
        for x in range( (row//3)*3, (row//3)*3 + 3 ):
            for y in range( (col//3)*3, (col//3)*3 + 3 ):
                if self.grid[ x ][ y ] == 0: result.add( x * 9 + y )

        return set( result ) 

    
    def getNextCell( self ):
        self.nextCellWeights = {}
        for id in self.empty_cells:
            self.nextCellWeights[ id ] = 0

        self.nextCellWeights_1( 1000 ) 
        self.nextCellWeights_2( 1 )

        return min( self.nextCellWeights, key = self.nextCellWeights.get )

    def nextCellWeights_A( self, _factor ): 
        for id in self.nextCellWeights:
            self.nextCellWeights[ id ] += id * _factor

    def nextCellWeights_B( self, _factor ): 
        self.nextCellWeights_A( _factor * -1 )

    def nextCellWeights_C( self, _factor ): 
        for id in self.nextCellWeights:
            self.nextCellWeights[ id ] += random.randint( 0, 999 ) * _factor

    def nextCellWeights_D( self, _factor ): 
        for id in self.nextCellWeights:
            self.nextCellWeights[ id ] += self.centerWeights[ id ] * _factor

    def nextCellWeights_E( self, _factor ): 
        for id in self.nextCellWeights:
            self.nextCellWeights[ id ] += len( self.getChoices( id ) ) * _factor

    def nextCellWeights_F( self, _factor ): 
        self.nextCellWeights_E( _factor * -1 )

    def nextCellWeights_G( self, _factor ): 
        for id in self.nextCellWeights:
            self.nextCellWeights[ id ] += len( self.getRelatedBlankCells( id ) ) * _factor

    def nextCellWeights_H( self, _factor ): 
        self.nextCellWeights_G( _factor * -1 )

    def nextCellWeights_I( self, _factor ): 
        for id in self.nextCellWeights:
            weight = 0
            for check in range( 81 ):
                if self.getCell( check ) != 0:
                    weight += math.sqrt( ( id//9 - check//9 )**2 + ( id%9 - check%9 )**2 )

    def nextCellWeights_J( self, _factor ): 
        self.nextCellWeights_I( _factor * -1 )

    def nextCellWeights_K( self, _factor ): 
        for id in self.nextCellWeights:
            weight = 0
            for id_blank in self.getRelatedBlankCells( id ):
                weight += len( self.getChoices( id_blank ) )
            self.nextCellWeights[ id ] += weight * _factor

    def nextCellWeights_L( self, _factor ): 
        self.nextCellWeights_K( _factor * -1 )



    
    def getChoices( self, _id ):
        available_choices = {1,2,3,4,5,6,7,8,9}
        row = _id // 9
        col = _id % 9

       
        for y in range( 0, 9 ):
            if self.grid[ row ][ y ] in available_choices:
                available_choices.remove( self.grid[ row ][ y ] )

       
        for x in range( 0, 9 ):
            if self.grid[ x ][ col ] in available_choices:
                available_choices.remove( self.grid[ x ][ col ] )

        
        for x in range( (row//3)*3, (row//3)*3 + 3 ):
            for y in range( (col//3)*3, (col//3)*3 + 3 ):
                if self.grid[ x ][ y ] in available_choices:
                    available_choices.remove( self.grid[ x ][ y ] )

        if len( available_choices ) == 0: return set()
        else: return set( available_choices ) 

    def nextChoice( self ):
        self.nextChoiceWeights = {}
        for i in self.choices[ self.current_cell ]:
            self.nextChoiceWeights[ i ] = 0

        self.nextChoiceWeights_1( 1000 )
        self.nextChoiceWeights_2( 1 )

        self.current_choice = min( self.nextChoiceWeights, key = self.nextChoiceWeights.get )
        self.setCell( self.current_cell, self.current_choice )
        self.choices[ self.current_cell ].remove( self.current_choice )

    def nextChoiceWeights_0( self, _factor ): 
        for i in self.nextChoiceWeights:
            self.nextChoiceWeights[ i ] += i * _factor

    def nextChoiceWeights_1( self, _factor ): 
        self.nextChoiceWeights_0( _factor * -1 )

    def nextChoiceWeights_2( self, _factor ): 
        for i in self.nextChoiceWeights:
            self.nextChoiceWeights[ i ] += random.randint( 0, 999 ) * _factor

    def nextChoiceWeights_3( self, _factor ): 
        self.digit_heuristic = { 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0 }
        for id in range( 81 ):
            if self.getCell( id ) != 0: self.digit_heuristic[ self.getCell( id ) ] += 1
        for i in self.nextChoiceWeights:
            self.nextChoiceWeights[ i ] += self.digit_heuristic[ i ] * _factor

    def nextChoiceWeights_4( self, _factor ): 
        self.nextChoiceWeights_3( _factor * -1 )

    def nextChoiceWeights_5( self, _factor ): 
        cell_choices = {}
        for id in self.getRelatedBlankCells( self.current_cell ):
            cell_choices[ id ] = self.getChoices( id )

        for c in self.nextChoiceWeights:
            weight = 0
            for id in cell_choices:
                weight += len( cell_choices[ id ] )
                if c in cell_choices[ id ]: weight -= 1
            self.nextChoiceWeights[ c ] += weight * _factor

    def nextChoiceWeights_6( self, _factor ): 
        self.nextChoiceWeights_5( _factor * -1 )

    def nextChoiceWeights_7( self, _factor ): 
        cell_choices = {}
        for id in self.getRelatedBlankCells( self.current_cell ):
            cell_choices[ id ] = self.getChoices( id )

        for c in self.nextChoiceWeights:
            weight = 0
            for id in cell_choices:
                if c in cell_choices[ id ]: weight += 1
            self.nextChoiceWeights[ c ] += weight * _factor

    def nextChoiceWeights_8( self, _factor ): 
        self.nextChoiceWeights_7( _factor * -1 )

    def nextChoiceWeights_9( self, _factor ): 
        cell_choices = {}
        for id in range( 81 ):
            if self.getCell( id ) == 0:
                cell_choices[ id ] = self.getChoices( id )

        for c in self.nextChoiceWeights:
            weight = 0
            for id in cell_choices:
                if c in cell_choices[ id ]: weight += 1
            self.nextChoiceWeights[ c ] += weight * _factor

    def nextChoiceWeights_a( self, _factor ): 
        self.nextChoiceWeights_9( _factor * -1 )



  
    def solve( self, _nextCellMethod, _nextChoiceMethod, _start_time, _prefillSingleChoiceCells = False ):
        s = self
        s.reset()

       
        if _nextCellMethod[ 0 ] in "ABCDEFGHIJKLMN":
            s.nextCellWeights_1 = getattr( s, "nextCellWeights_" + _nextCellMethod[0] )
        elif _nextCellMethod[ 0 ] == " ":
            s.nextCellWeights_1 = lambda x: None
        else:
            print( "(A) Incorrect optimization parameters provided" )
            return False

        if len( _nextCellMethod ) > 1:
            if _nextCellMethod[ 1 ] in "ABCDEFGHIJKLMN":
                s.nextCellWeights_2 = getattr( s, "nextCellWeights_" + _nextCellMethod[1] )
            elif _nextCellMethod[ 1 ] == " ":
                s.nextCellWeights_2 = lambda x: None
            else:
                print( "(B) Incorrect optimization parameters provided" )
                return False
        else:
            s.nextCellWeights_2 = lambda x: None

   
        if _nextChoiceMethod[ 0 ] in "0123456789a":
            s.nextChoiceWeights_1 = getattr( s, "nextChoiceWeights_" + _nextChoiceMethod[0] )
        elif _nextChoiceMethod[ 0 ] == " ":
            s.nextChoiceWeights_1 = lambda x: None
        else:
            print( "(C) Incorrect optimization parameters provided" )
            return False

        if len( _nextChoiceMethod ) > 1:
            if _nextChoiceMethod[ 1 ] in "0123456789a":
                s.nextChoiceWeights_2 = getattr( s, "nextChoiceWeights_" + _nextChoiceMethod[1] )
            elif _nextChoiceMethod[ 1 ] == " ":
                s.nextChoiceWeights_2 = lambda x: None
            else:
                print( "(D) Incorrect optimization parameters provided" )
                return False
        else:
            s.nextChoiceWeights_2 = lambda x: None

       
        if _prefillSingleChoiceCells == True:
            while True:
                next = False
                for id in range( 81 ):
                    if s.getCell( id ) == 0:
                        cell_choices = s.getChoices( id )
                        if len( cell_choices ) == 1:
                            c = cell_choices.pop()
                            s.setCell( id, c )
                            next = True
                if not next: break

        
        for x in range( 0, 9, 1 ):
            for y in range( 0, 9, 1 ):
                if s.grid[ x ][ y ] == 0:
                    s.empty_cells.add( 9*x + y )
        s.empty_cells_initial = set( s.empty_cells ) 

        
        for id in s.empty_cells:
            s.search_space *= len( s.getChoices( id ) )

        
        if len( s.empty_cells ) < 1:
            if s.validate():
                print( "Sudoku provided is valid!" )
                return True
            else:
                print( "Sudoku provided is not valid!" )
                return False
        else: s.current_cell = s.getNextCell()

        s.choices[ s.current_cell ] = s.getChoices( s.current_cell )
        if len( s.choices[ s.current_cell ] ) < 1:
            print( "(C) Sudoku cannot be solved!" )
            return False



        
        while True:
            

            s.iterations += 1

            
            if s.empty_cells == s.empty_cells_initial and len( s.choices[ s.current_cell ] ) < 1:
                print( "(A) Sudoku cannot be solved!" )
                return False

            
            if len( s.empty_cells ) < 1:
                if s.validate():
                    print( "Sudoku has been solved! " )
                    print( "search space is {}".format( self.search_space ) )
                    print( "empty cells: {}, iterations: {}, backtrack iterations: {}".format( len( self.empty_cells_initial ), self.iterations, self.iterations_backtrack ) )
                    for i in range(9):
                        print( self.grid[i] )
                    return True

            
            if len( s.empty_cells ) > 0:

                s.current_cell = s.getNextCell() 
                s.history.append( s.current_cell ) 
                s.empty_cells.remove( s.current_cell ) 
                s.choices[ s.current_cell ] = s.getChoices( s.current_cell ) 

                if len( s.choices[ s.current_cell ] ) > 0: 
                    s.nextChoice()
                    continue

            
            if len( s.choices[ s.current_cell ] ) > 0 and ( s.empty_cells == s.empty_cells_initial or len( s.empty_cells ) < 1 ): 
                s.nextChoice()
                continue

           
            s.history.remove( s.current_cell ) 
            s.empty_cells.add( s.current_cell ) 
            del s.choices[ s.current_cell ] 
            s.current_choice = 0
            s.setCell( s.current_cell, s.current_choice ) 

            
            while True:
                s.iterations_backtrack += 1

                if len( s.history ) < 1:
                    print( "(B) Sudoku cannot be solved!" )
                    return False

                s.current_cell = s.history[ -1 ] 

                if len( s.choices[ s.current_cell ] ) < 1: 
                    s.history.remove( s.current_cell )
                    s.empty_cells.add( s.current_cell )
                    s.current_choice = 0
                    del s.choices[ s.current_cell ]
                    s.setCell( s.current_cell, s.current_choice )
                    continue

                
                s.nextChoice()
                break 

    

    

    

