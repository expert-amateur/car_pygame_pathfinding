# car_pygame_pathfinding
2D PyGame Implementation of path finding with obstacles for a non holonomic car

Demo:
![car_demo_gif](https://github.com/expert-amateur/car_pygame_pathfinding/assets/103503974/8ad195d2-bc81-4edb-97f6-092ade89477a)

Includes:
1) Implementation of hybrid A-star
2) Kinematically consistent paths
3) Collision detection using separating axis theorem

Future changes:
1) Speed up algorithm (demo took 2 min for path finding)
   a) Currently checking collision with all obstacles at every new state. Narrow it down by checking only within a small area
   b) Make the algorithm greedier (higher coefficient for h val)
   c) Use probabilistic methods for checkpoints
2) Smooth interpolation between states
3) Other types of nonholonomic vehicles

NOTE: File may not run correctly simce it was implemented using VS Code's Jupyter extension. If any problems occur, use https://pypi.org/project/ipynb-py-convert/ to convert to .ipynb
