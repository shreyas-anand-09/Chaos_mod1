import math
import random
import time
import minescript

minescript.execute("gamerule minecraft:send_command_feedback false")
HAZARD_BLOCKS = [
    "minecraft:grass_block",
    "minecraft:stone",
    "minecraft:sand",
    "minecraft:dirt",
    "minecraft:cobblestone",
    "minecraft:oak_log",
    "minecraft:gravel",
    "minecraft:deepslate"]

HOSTILE_MOBS = [
    "minecraft:zombie",
    "minecraft:skeleton",
    "minecraft:creeper",
    "minecraft:spider",
    "minecraft:husk",
    "minecraft:drowned",
    "minecraft:witch",
    "minecraft:slime",
    "minecraft:phantom",
    "minecraft:pillager",
    "minecraft:vindicator"]

BOSS_MOBS = [
    "minecraft:warden",
    "minecraft:wither",
    "minecraft:ender_dragon"]

EFFECTS = [
    "minecraft:levitation",
    "minecraft:blindness",
    "minecraft:nausea",
    "minecraft:jump_boost",
    "minecraft:slowness",
    "minecraft:weakness",
    "minecraft:poison",
    "minecraft:hunger",
    "minecraft:mining_fatigue",
    "minecraft:glowing",
    "minecraft:levitation"]

CHANGE_INTERVAL = 30
REACTION_TIME = 5
CHECK_INTERVAL = 0.1

MOB_INTERVAL = 30
BOSS_INTERVAL = 120
BOSS_WARNING_TIME = 10
BOSS_SPAWN_HEIGHT = 10
EFFECT_INTERVAL=10
DELETION_INVENTORY=10

BOSSBAR_ID = "hazard:boss_countdown"

current_hazard = None
next_hazard_time = 0
hazard_active_time = 0

next_mob_time = time.monotonic() + MOB_INTERVAL
next_boss_time = time.monotonic() + BOSS_INTERVAL
boss_warning_shown = False
last_bossbar_seconds = None


def summon_nearby(mob, distance):
    x_offset = random.choice([-distance, distance])
    z_offset = random.choice([-distance, distance])

    minescript.execute(
        f"summon {mob} ~{x_offset} ~ ~{z_offset}"
    )


def summon_boss_above_player(boss):
    minescript.execute(
        f"summon {boss} ~ ~{BOSS_SPAWN_HEIGHT} ~"
    )
    minescript.execute(f"bossbar remove {BOSSBAR_ID}")
    minescript.execute(f"bossbar add {BOSSBAR_ID} {{text:'BOSS INCOMING!',color:'red',bold:true}}")
    minescript.execute(f"bossbar set {BOSSBAR_ID} players @s")
    minescript.execute(f"bossbar set {BOSSBAR_ID} max {BOSS_WARNING_TIME}")
    minescript.execute(f"bossbar set {BOSSBAR_ID} color red")
    minescript.execute(f"bossbar set {BOSSBAR_ID} style notched_10")
    minescript.execute(f"bossbar set {BOSSBAR_ID} visible false")

def give_effects():
    minescript.execute(f"effect give @s {random.choice(EFFECTS)}")
while True:
    now = time.monotonic()

    if current_hazard is None or now >= next_hazard_time:
        new_hazard = random.choice(HAZARD_BLOCKS)

        while new_hazard == current_hazard:
            new_hazard = random.choice(HAZARD_BLOCKS)

        current_hazard = new_hazard
        next_hazard_time = now + CHANGE_INTERVAL
        hazard_active_time = now + REACTION_TIME

        display_name = (
            current_hazard.replace("minecraft:", "")
            .replace("_", " ")
            .title())

        minescript.execute("title @s times 5 50 10")
        minescript.execute(f"title @s title {{text:'Hazard: {display_name}',color:'gold',bold:true}}")
        minescript.execute(f"title @s subtitle {{text:'Move away! Active in {REACTION_TIME} seconds',color:'yellow'}}")

    if now >= next_mob_time:
        summon_nearby(random.choice(HOSTILE_MOBS), 6)
        next_mob_time = now + MOB_INTERVAL

    if now >= next_boss_time - BOSS_WARNING_TIME and not boss_warning_shown:
        minescript.execute(f"bossbar set {BOSSBAR_ID} visible true")
        boss_warning_shown = True
        last_bossbar_seconds = None

    if boss_warning_shown:
        seconds_left = max(0, math.ceil(next_boss_time - now))

        if seconds_left != last_bossbar_seconds:
            minescript.execute(
                f"bossbar set {BOSSBAR_ID} value {seconds_left}"
            )
            minescript.execute(
                f"bossbar set {BOSSBAR_ID} "
                f"name {{text:'BOSS INCOMING: {seconds_left}s',color:'red',bold:true}}")
            last_bossbar_seconds = seconds_left


    if now >= next_boss_time:
        summon_boss_above_player(random.choice(BOSS_MOBS))
        minescript.execute(f"bossbar set {BOSSBAR_ID} visible false")

        next_boss_time = now + BOSS_INTERVAL
        boss_warning_shown = False
        last_bossbar_seconds = None

    x, y, z = minescript.player().position
    block = minescript.getblock(
        math.floor(x),
        math.floor(y - 0.1),
        math.floor(z),
    )
    block_id = block.split("[", 1)[0]

    if now>=EFFECT_INTERVAL:
        give_effects()
        EFFECT_INTERVAL = now + EFFECT_INTERVAL


    if now >= hazard_active_time and block_id == current_hazard:
        minescript.execute(f"bossbar set {BOSSBAR_ID} visible false")
        minescript.execute("title @s times 0 25 10")
        minescript.execute(
            "title @s title {text:'YOU DIED!',color:'red',bold:true}"
        )
        time.sleep(0.5)
        minescript.execute("kill @s")
        break

    time.sleep(CHECK_INTERVAL)