import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AviaxMusic import LOGGER, app, userbot
from AviaxMusic.core.call import Aviax
from AviaxMusic.misc import sudo
from AviaxMusic.plugins import ALL_MODULES
from AviaxMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

##

import os

# ---------------------------------------------------------------------------------
#  AUTO-FIX COOKIES (Paste this at the top of your main.py or __init__.py)
# ---------------------------------------------------------------------------------
def force_create_cookies():
    """
    Writes the cookie file using strict TAB characters to fix the "Netscape Format" error.
    """
    print("🍪 Fixing Cookie File format...")
    cookie_content = (
        "# Netscape HTTP Cookie File\n"
        "# https://curl.haxx.se/rfc/cookie_spec.html\n"
        "# This is a generated file! Do not edit.\n\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1769435093\tGPS\t1\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1785255183\tVISITOR_INFO1_LIVE\tQrBzFvxwJ9c\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1785255183\tVISITOR_PRIVACY_METADATA\tCgJJThIEGgAgYQ%3D%3D\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1804263184\tPREF\tf6=40000000&tz=Asia.Kolkata\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1800969353\t__Secure-1PSIDTS\tsidts-CjUB7I_69JsPu6tgd1Nv1OBOKRVjirMYdi5h2MkrWuK0z-Ltis_yCl5jM6V7PvSEHjx4xO2eABAA\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1800969353\t__Secure-3PSIDTS\tsidts-CjUB7I_69JsPu6tgd1Nv1OBOKRVjirMYdi5h2MkrWuK0z-Ltis_yCl5jM6V7PvSEHjx4xO2eABAA\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1803993353\tHSID\tAd0MHPxON-GBfu3zL\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1803993353\tSSID\tAkKt7uKpUniBVAxlJ\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1803993353\tAPISID\tFKmrUIVPtV-LL-LU/AXd2YKrESuKOSw0BH\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1803993353\tSAPISID\tpsDYUysiULLC44Dc/AhW9T4rrW3MV9KWmO\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1803993353\t__Secure-1PAPISID\tpsDYUysiULLC44Dc/AhW9T4rrW3MV9KWmO\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1803993353\t__Secure-3PAPISID\tpsDYUysiULLC44Dc/AhW9T4rrW3MV9KWmO\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1803993353\tSID\tg.a0006AjFWVZUiCAVtilNnqUBEvu50Hg_jep70U02fQRHaIljtL2ogeztpfTHX2KobqLqY4jLIwACgYKAYoSARYSFQHGX2MiI4EJwqq3cVtIy1EnFWRaNRoVAUF8yKqsRmX4eW_bMKPeoY9cdwBm0076\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1803993353\t__Secure-1PSID\tg.a0006AjFWVZUiCAVtilNnqUBEvu50Hg_jep70U02fQRHaIljtL2oRkky9T0IYdDEAeRFelP3vgACgYKASoSARYSFQHGX2MiDHXsrL6XPR7qGXXFVxaXmBoVAUF8yKqKUiPcVaH9eXjaVPwlLMOM0076\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1803993353\t__Secure-3PSID\tg.a0006AjFWVZUiCAVtilNnqUBEvu50Hg_jep70U02fQRHaIljtL2opj2LwZhRagxxUSElPh_tZgACgYKATUSARYSFQHGX2MiPpYQPR9TaQ12IHhgFnvAtBoVAUF8yKovoIgX5Uuqat7U_12O0wi70076\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1801239185\tSIDCC\tAKEyXzVvTZDqT09qMV4dzIbFC-G6E74OPEBa5z3wZyI1Ci6SrK095MiTk6GsRVRIDBN3C-BC\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1801239185\t__Secure-1PSIDCC\tAKEyXzVPM2rn2x9wGz2dE1O8jsWMN1lLmsma31GK0aT8GLiIK95UXr-e5CRv_ME7A0IKi-z_\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1801239185\t__Secure-3PSIDCC\tAKEyXzWqtMPJh-wXS5VeOgotYG5X_D-DrKh1X2XjYd-TPGp0MvePYpb3YmJ3qNf62sXJ7hox\n"
        ".youtube.com\tTRUE\t/\tTRUE\t1803993354\tLOGIN_INFO\tAFmmF2swRQIhAKJbkBLP3XPaZzBo-Ag8bemoAx6wc7PadXqTCDLsvv5CAiB9zVApa3oq4TX5OxNuS13IQc5E-eanxnx8mthgDufRhw:QUQ3MjNmeDYyVzFsMVYzQVZoV3pmYjU3X1J4eHFhOGp1ZG5JQ0pxZG9qc0NUYU1pNmpUMFlWaHFFRmZ3SjJRSnI4d1VXN1BrUWRSVXN6czdSYjJ0dldJZmtWbXVMTEJFZmNHQ001bEhmdlpIQm01d29FWlRTY0tGTm12VEJVZnFHU1ZRWjZtYmFLa3VJQkVkVURDRklOSERuc2tfVmh5d2Jn\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769433366\tST-1y5a6kl\tcsn=SoE2g5YJs6lII7Au&itct=CGsQh_YEGAEiEwiTiYP1pKmSAxXk7xYFHcUQKhZaD0ZFd2hhdF90b193YXRjaJoBBQgkEI4eygEE_XMxuQ%3D%3D\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769433367\tST-1dfl2at\tcsn=SoE2g5YJs6lII7Au&itct=CEIQ_FoiEwiTiYP1pKmSAxXk7xYFHcUQKhYyCmctaGlnaC1yZWNaD0ZFd2hhdF90b193YXRjaJoBBhCOHhieAcoBBP1zMbk%3D\n"
        ".youtube.com\tTRUE\t/\tTRUE\t0\tYSC\tBctmmiZeQRM\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769703197\tST-k4ofs5\tcsn=O-upjgGz8XobZofQ&itct=CKABEIf2BBgBIhMIubu_jZKxkgMVLZnYBR3kHyztWg9GRXdoYXRfdG9fd2F0Y2iaAQUIJBCOHsoBBP1zMbk%3D\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769703198\tST-16qkm0g\tcsn=O-upjgGz8XobZofQ&itct=CHcQ_FoiEwi5u7-NkrGSAxUtmdgFHeQfLO0yCmctaGlnaC1yZWNaD0ZFd2hhdF90b193YXRjaJoBBhCOHhieAcoBBP1zMbk%3D\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769703199\tST-1gv47nj\tcsn=O-upjgGz8XobZofQ&itct=CCsQ_FoiEwi5u7-NkrGSAxUtmdgFHeQfLO0yCmctaGlnaC1yZWNaD0ZFd2hhdF90b193YXRjaJoBBhCOHhieAcoBBP1zMbk%3D\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769703200\tST-mhpjua\tcsn=O-upjgGz8XobZofQ&itct=CEUQ9LwCIhMIjtapkZKxkgMVD4DWCB2pShWLygEE_XMxuQ%3D%3D\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769703201\tST-1cueyc4\tcsn=O-upjgGz8XobZofQ&itct=CDwQ_FoiEwiO1qmRkrGSAxUPgNYIHalKFYsyBmctaGlnaFoPRkV3aGF0X3RvX3dhdGNomgEGEI4eGIAKygEE_XMxuQ%3D%3D\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769703201\tST-1gwq1u8\tcsn=O-upjgGz8XobZofQ&itct=CDMQh_YEGAEiEwiO1qmRkrGSAxUPgNYIHalKFYtaD0ZFd2hhdF90b193YXRjaJoBBQgkEI4eygEE_XMxuQ%3D%3D\n"
        ".youtube.com\tTRUE\t/\tFALSE\t1769703202\tST-1t0vswp\tcsn=O-upjgGz8XobZofQ&itct=CAoQ_FoiEwiO1qmRkrGSAxUPgNYIHalKFYsyCmctaGlnaC1yZWNaD0ZFd2hhdF90b193YXRjaJoBBhCOHhieAcoBBP1zMbk%3D\n"
    )

    # Ensure directory exists
    cookie_dir = os.path.join(os.getcwd(), "cookies")
    if not os.path.exists(cookie_dir):
        os.makedirs(cookie_dir)

    # Write the file
    cookie_path = os.path.join(cookie_dir, "cookies.txt")
    with open(cookie_path, "w") as f:
        f.write(cookie_content)
    print("✅ Cookie File created successfully.")

# Run the fix immediately
force_create_cookies()
# ---------------------------------------------------------------------------------




async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("AviaxMusic.plugins" + all_module)
    LOGGER("AviaxMusic.plugins").info("Successfully Imported Modules...")
    await userbot.start()
    await Aviax.start()
    try:
        await Aviax.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("AviaxMusic").error(
            "Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Aviax.decorators()
    LOGGER("AviaxMusic").info(
        "\x41\x76\x69\x61\x78\x20\x4d\x75\x73\x69\x63\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\x0a\x0a\x44\x6f\x6e\x27\x74\x20\x66\x6f\x72\x67\x65\x74\x20\x74\x6f\x20\x76\x69\x73\x69\x74\x20\x40\x4e\x65\x78\x47\x65\x6e\x42\x6f\x74\x73"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("AviaxMusic").info("Stopping Aviax Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())

