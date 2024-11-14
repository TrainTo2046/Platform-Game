### 1. **Platform-Game**
- This is a simple platformer game created in python using the pygame module.

### 2. **Introduction**
   - The goals of this project were:
        - Improve Object Oriented Programming skills in python.
            - creating resuable classes for entities such as player, enemies, and other interactable objects.
            - making different instances of different classes interact with eachother.
        - Learn and utilize the pygame module (python wrapper for SDL).
            - designing a display where the game takes place.
            - update the display as the game progresses.
            - take user inputs and translate them into game procedure.
    - This project follows the platformer project created by DaFluffyPotato.

### 3. **What I Learned**
   - Tile Map and Collision Detection:
        - Create tile map based on rectangle objects for the platformer.
        - Placing two or more rectangle object in the game space and detect if any of them collide with eachother. 
   - Physics and Movement:
        - Implement gravity, jumping, and movement physics on player object.
        - Implement player movement left and right so they can interact with other non-player objects in the map.
   - Entities and Game Objects:
        - Create reusable classes for enemies, and other interactable objects such as enemy weapons.
   - Effects and Animation:
        - Add particle effects such sparks during collisions, and background.
        - Animation for Player entities such as idle, walk, dash, jump, slide.
        - Animation for Enemy entities such as idle, walk, attack.
   - Camera and Parallax Scrolling:
        - Implement a camera system that follows the player.
        - Implement a background and foreground tile that allows parallax effect with player movement.
   - Enemies Behaviour: 
        - Design enemies behaviour to attack player and protect their territory.
   - Level Editor and Transitions: 
        - Implement a Level Editor for easy creation of levels using tile assets loaded into the program.
        - Program allows saving the level as a json file and importing into the game for use.
        - Create transition between different levels, enabling a multi-level game.

### 4. **Challenges I Faced**
   - Implementing interactions between different entities
        - As more elements were being added to the game, it was difficult ot keep track of all the elements and know how they related to each other.
        - For example: Adding a projectile attck to Enemy entity.
            - You have to consider all the ways the projectile interacts in the game and with the environemnt.
            - It involves figuring out when the projectile attack happens, and the movement direction.
            - Also have to consider what happens when it hits a  wall, a player, or goes out of map.
        - All these are different elements that must to taken into account when making changes to one single entity was challenging.
   - Implementing mathemathical concepts for movement of objects was not easy to grasp.
        - Every movement in the game is manually controlled so they have to accounted for a seamless flow.
        - For example: Player Movement was tricky at first.
            - Movement in the horizontal axis involved calcuating the x-axis velocity of player and using it to position the palyer in the proper place
            - Movement in the vertical axis involved calcuating the y-axis velocity of player and using it to position the palyer in the proper place
            - Dash movement involved, hiding player for multiple frames.
            - The camera movement also follows the player so, a offest had to created and used in player movement calculation

### 5. **Project Showcase**
   - The program that was build at the end of this learning experience can be played by cloning this repo and running the game.py file.
   - Perequsits: have python and pygames installed in your deviceIf the tutorial involved building a project, showcase what you built. Include any relevant screenshots, links, or demos.

### 6. **Next Steps**
   Now that I have a good understanding of Pygame, I plan to:
   - Expand the game: 
        - Add more levels, features, and polish to create a complete game.
        - Add more player and enemy attack types.
   - Experiment with AI:
        - Add more complex AI behaviors and enemy types.
   - Optimize performance:
        - Use more advanced optimization techniques for smoother gameplay.

### 7. **Resource**
   - This project follows the Pygame Platformer project created by DaFluffyPotato.
   - If you're interested in learning about this project more, you can find it [here](https://dafluffypotato.com/assets/pg_tutorial).

---