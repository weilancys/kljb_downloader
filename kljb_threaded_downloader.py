from selenium import webdriver
from urllib.request import urlretrieve
import time
from datetime import timedelta, datetime
import os
import threading
import logging
import argparse
import sys

BASE_FOLDER_NAME = "可乐加冰"
results = {}
startTime = None
endTime = None

kljb_collection = {
	"season_1": { "season_id": 1, "main_page": "https://www.ysts8.com/Yshtml/Ys15979.html", "url_template": "https://www.ysts8.com/play_15979_49_1_{}.html", "number_of_episodes": 153 }, 
	"season_2": { "season_id": 2, "main_page": "https://www.ysts8.com/Yshtml/Ys15972.html", "url_template": "https://www.ysts8.com/play_15972_49_1_{}.html", "number_of_episodes": 158 }, 
	"season_3": { "season_id": 3, "main_page": "https://www.ysts8.com/Yshtml/Ys16033.html", "url_template": "https://www.ysts8.com/play_16033_50_1_{}.html", "number_of_episodes": 182 }, 
	"season_4": { "season_id": 4, "main_page": "https://www.ysts8.com/Yshtml/Ys16034.html", "url_template": "https://www.ysts8.com/play_16034_50_1_{}.html", "number_of_episodes": 183 }, 
	"season_5": { "season_id": 5, "main_page": "https://www.ysts8.com/Yshtml/Ys16035.html", "url_template": "https://www.ysts8.com/play_16035_50_1_{}.html", "number_of_episodes": 185 }, 
	"season_6": { "season_id": 6, "main_page": "https://www.ysts8.com/Yshtml/Ys16036.html", "url_template": "https://www.ysts8.com/play_16036_50_1_{}.html", "number_of_episodes": 180 }, 
	"season_7": { "season_id": 7, "main_page": "https://www.ysts8.com/Yshtml/Ys16080.html", "url_template": "https://www.ysts8.com/play_16080_51_1_{}.html", "number_of_episodes": 186 }, 
	"season_8": { "season_id": 8, "main_page": "https://www.ysts8.com/Yshtml/Ys16084.html", "url_template": "https://www.ysts8.com/play_16084_51_1_{}.html", "number_of_episodes": 179 }, 
	"season_9": { "season_id": 9, "main_page": "https://www.ysts8.com/Yshtml/Ys16129.html", "url_template": "https://www.ysts8.com/play_16129_51_1_{}.html", "number_of_episodes": 186 }, 
	"season_10": { "season_id": 10, "main_page": "https://www.ysts8.com/Yshtml/Ys16157.html", "url_template": "https://www.ysts8.com/play_16157_51_1_{}.html", "number_of_episodes": 165 }, 
	"season_11": { "season_id": 11, "main_page": "https://www.ysts8.com/Yshtml/Ys16204.html", "url_template": "https://www.ysts8.com/play_16204_51_1_{}.html", "number_of_episodes": 117 }, 
}


def parseArgs():
	try:
		parser = argparse.ArgumentParser()
		parser.add_argument("season", help="specify which season to download\neg: 2 or 3,5,6 or 2-7\nrange 1-11 with 0 meaning all seasons.")
		args = parser.parse_args()

		if "-" in args.season:		
			startIndex, endIndex = args.season.split("-")
			startIndex = int(startIndex)
			endIndex = int(endIndex)
			if startIndex > endIndex:
				raise ValueError("season index disorder.")
			if startIndex < 0 or endIndex > len(kljb_collection):
				raise ValueError("season index out of range.")
			season_list = [ season for season in range(startIndex, endIndex+1) ]
		elif "," in args.season:
			season_list = [ int(season.strip()) for season in args.season.split(",")]
		else:
			if int(args.season) == 0:
				season_list = [ season for season in range(1, len(kljb_collection)+1) ]
			else:
				season_list = [ int(args.season) ]
	except:
		return []
	else:
		return season_list

def preDownload(season_list):
	global BASE_FOLDER_NAME
	global kljb_collection
	global results

	logging.basicConfig(filename="kljb_threaded_downloader.log", level=logging.DEBUG, format="%(levelname)s -- %(asctime)s -- %(message)s")
	
	for season in season_list:
		try:
			subFolderName = BASE_FOLDER_NAME + str(season)
			os.makedirs(os.path.join(BASE_FOLDER_NAME, subFolderName))
		except FileExistsError:
			pass
		for s in kljb_collection:
			if season == kljb_collection[s]["season_id"]:
				_season = kljb_collection[s]

		results[season] = { episode: None for episode in range(1, _season["number_of_episodes"]+1) }

def download(season_list):
	global kljb_collection
	global startTime
	global endTime

	startTime = time.time()

	def _thread_worker(episode, semaphore):
		nonlocal url_template
		nonlocal store_path
		nonlocal season
		url = url_template.format(episode)

		with semaphore:
			for trial in range(3):
				try:
					driver = webdriver.Chrome()
					driver.get(url)
					driver.switch_to.frame("play")
					audio_element = driver.find_element_by_id("jp_audio_0")
					link = audio_element.get_attribute("src")
					
					urlretrieve(link, os.path.join(store_path, "{:03d}.mp3".format(episode)))
				except UnboundLocalError as ule:
					#this exception specifically is catched if chrome doesn't get started in the first place
					results[season][episode] = False
					logging.debug("fail at season{} episode {} with url: {}. Error Message: {}\n".format(season, episode, url, str(ule)))
				except Exception as e:
					results[season][episode] = False
					logging.debug("fail at season{} episode {} with url: {}. Error Message: {}\n".format(season, episode, url, str(e)))
					driver.quit()
				else:
					results[season][episode] = True
					logging.debug("success at season{} episode {}.\n".format(season, episode))
					driver.quit()
					break

	for season in season_list:
		for s in kljb_collection:
			if season == kljb_collection[s]["season_id"]:
				url_template = kljb_collection[s]["url_template"]
				number_of_episodes = kljb_collection[s]["number_of_episodes"]
				store_path = os.path.join(BASE_FOLDER_NAME, BASE_FOLDER_NAME + str(season))

		semaphore = threading.Semaphore(4)

		for episode in range(1, number_of_episodes+1):
			t = threading.Thread(target=_thread_worker, args=(episode, semaphore))
			time.sleep(0.1)
			t.start()

		for thread in threading.enumerate():
			if thread is threading.main_thread():
				continue
			thread.join()

	endTime = time.time()

def timeFormat(ts):
	return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
			
def report():
	global startTime
	global endTime

	with open("download_report.txt", "w") as logFile:
		for season_id in results:
			logFile.write("season " + str(season_id) + ": ")
			successCounter = 0
			for r in results[season_id].values():
				if r:
					successCounter += 1
			logFile.write("{}/{}\n".format(successCounter, len(results[season_id])))
			if not all(results[season_id].values()):
				for episode_id in results[season_id]:
					if results[season_id][episode_id]:
						logFile.write("{} -- success\n".format(episode_id))
					else:
						logFile.write("{} -- fail\n".format(episode_id))
			logFile.write("="*50)
			logFile.write("\n")

		logFile.write("download started at {}\nfinished at {}\ntotal time:{}\n".format(timeFormat(startTime), timeFormat(endTime), str(timedelta(seconds=int(endTime - startTime)))))
			

if __name__ == '__main__':
	season_list = parseArgs()
	if not season_list:
		print("invalid arguments, see -h or --help for help messages.")
		sys.exit()

	preDownload(season_list)
	download(season_list)
	report()
	