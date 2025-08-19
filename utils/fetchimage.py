from PIL import Image
import requests
from io import BytesIO

def merge_icons(mods):
    base_url = "https://img.littlezhaidi.me/" #我這裡的圖片是32x32的大小，ch.tetr.io/res/zenith-mods/的圖片是183x183的大小，這樣放在embed裡面比較好看
    icons = []

    SPECIAL_COMBOS = {
    "swamp_water": ['allspin', 'invisible', 'doublehole', 'volatile', 'gravity', 'messy', 'nohold', 'expert'],
    "emperors_decadence": ["expert", "doublehole", "nohold"],
    "divine_mastery": ["expert", "doublehole", "volatile", "messy"],
    "the_con_artist": ["expert", "volatile", "allspin"],
    "the_escape_artist": ["doublehole", "messy", "allspin"],
    "deadlock": ["nohold", "doublehole", "messy"],
    "the_starving_artist": ["nohold", "allspin"],
    "the_grandmaster": ["gravity", "invisible"],
    "a_modern_classic": ["nohold", "gravity"],
}
    # 檢查是否為特殊組合
    for combo_name, special_combo in SPECIAL_COMBOS.items():
        if set(mods) == set(special_combo):
            mods = [combo_name]
            print(f"Detected special combo: {combo_name}")
            break
        # If there are exactly 7 mods and "duo" is not among them, treat it as a "swamp_water_lite" combination
        elif len(mods) == 7 and "duo" not in mods:
            mods = ["swamp_water_lite"]
            print(f"Detected special combo: {combo_name}")
            break
        elif len(mods) == 1:
            break
    
    # 下載每個 mod 的圖標
    for mod in mods:
        response = requests.get(f"{base_url}{mod}.png")
        if response.status_code == 200:
            icons.append(Image.open(BytesIO(response.content)))

    # 計算合併後的圖片大小
    width = sum(icon.width for icon in icons)
    height = max(icon.height for icon in icons)

    # 建立空白圖片
    combined_image = Image.new("RGBA", (width, height))

    # 將每個圖標貼到空白圖片上
    x_offset = 0
    for icon in icons:
        combined_image.paste(icon, (x_offset, 0))
        x_offset += icon.width

    # 儲存合併後的圖片
    combined_image.save("combined.png")
    print("已儲存合併後的圖片")

# Example usage
if __name__ == "__main__":
    mods = ["nohold", "gravity"]
    merged_image_path = merge_icons(mods)