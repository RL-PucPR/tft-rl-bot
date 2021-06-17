from gym.envs.registration import register

register(
    id='tft-bot-v0',
    entry_point='tft_bot.envs:GameStateEnv',
)
