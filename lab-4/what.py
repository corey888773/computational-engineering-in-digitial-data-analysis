class Strategy:
    def __init__(self, name) -> None:
        self.strategy = self.set_strategy(name)
 
    def set_strategy(self, name):
        if name == "q_learning":
            return self.q_learning_strategy
        elif name == "player":
            return self.player_input_strategy
        else:
            return self.random_strategy
 
    def random_strategy(self, **kwargs):
        return kwargs["env"].action_space.sample()
    def q_learning_strategy(self, **kwargs):
        quantized_state = kwargs["q_learning"].quantize_state(kwargs["state"])
        return kwargs["q_learning"].get_best_action(quantized_state)
 
    def player_input_strategy(self,**kwargs):
        # from time import time
        # start = time()
        # while time() < start + 0.2:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return 0
                    if event.key == pygame.K_2:  
                        return 1
                    if event.key == pygame.K_3:  
                        return 2
                    if event.key == pygame.K_4:  
                        return 3

    def exec(self, **kwargs):
        return self.strategy(**kwargs)
 
if __name__ =='__main__':
    env = GridWorldEnv(render_mode='human')
    strategy = Strategy('player') 
    for i in range(1):
        state, _ = env.reset()
        done = False
        score = 0
        while not done:
            action = strategy.exec(env=env, state=state) 
            state, reward, terminated, truncated, info = env.step(action)
            print(state)
            score += reward
            done = terminated or truncated
            print(score)
    env.close()