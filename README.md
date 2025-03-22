# GT OMSCS ML4T Q-Learning Example

<i>Note: There is no code from the actual coursework included in this project. My QLearner implementation has been left out on purpose.</i>

This script enables a Q-Learner to learn and play Tic-Tac-Toe against the user. It is meant to be usable with the Qlearner that was created as part of CS7646, Machine Learning for Trading. Other students of the class can drop their Qlearner implementation in and play around with the parameters in order to create an effective Tic-Tac-Toe bot. 

After training your Qlearner, you can play some games against it to test how it performs. It will also continue to 'learn' from the games that you play. The learner is configured to always be Xs and always go first. 

The best case for the learner is to reach a point where it is incapable of losing since Tic-Tac-Toe is quite a bad game and the best you can hope to do against a competent opponent is play to a draw. 

## Details

The default parameters found in the tictactoe.py file should produce a learner that will never lose since every game will either result in the learner winning or a draw. To play, you simply enter a digit from 0 to 9 representing the position of the tile you wish to mark:

```
 0 | 1 | 2 
-----------
 3 | 4 | 5 
-----------
 6 | 7 | 8 
```

The state of the game is discretized as a 9 digit ternary number. For example the game board:

```
 X |   | O  --> 1 0 2
-----------
   | X |    --> 0 1 0
-----------
   |   | X  --> 0 0 1
```

Would be represented as the string:

```
"102010001"
```

When converted to base-10 this is equal to 8,101, which would be the discretized state that represents this unique game board. There are 3^9 (19,683) total possible states (ignoring invalid board states) and 9 actions, which correspond to placing a piece in any of the 9 spaces. 

During training, the learner chooses where it wants to move given the current state of the board. Then, the 'opponent' takes their move, which is a random choice between a random free space, or a space which would either complete a line to win or disrupt the learners line to win (default is 50/50 between the two). This is an attempt to explore as many states as possible, both randomly and with some strategic value. If the board state results in a win, loss, or draw, the epoch is terminated and a new game begins. If the learner tries to make an illegal move, it receives a negative reward signal and is prompted for a new move. 
