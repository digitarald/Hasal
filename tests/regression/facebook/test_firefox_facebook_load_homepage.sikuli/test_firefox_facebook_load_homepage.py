# if you are putting your test script folders under {git project folder}/tests/, it will work fine.
# otherwise, you either add it to system path before you run or hard coded it in here.
sys.path.append(sys.argv[2])
import os
import shutil
import browser
import common
import facebook

com = common.General()
ff = browser.Firefox()
fb = facebook.facebook()

ff.clickBar()
ff.enterLink(sys.argv[3])
com.screen_shot()
region = Region(int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9]))
img = capture(region)
shutil.move(img, os.path.join(sys.argv[4], sys.argv[5]))
type(Key.ENTER)

sleep(2)
fb.wait_for_loaded()
