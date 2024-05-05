# Converts legacy FNF charts to the new format
# Do what ever you want with this code, I don't care
# - GuglioIsStupid

import sys, os, json

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python convert_legacy_to_new.py <input json> <diffname> <old output>")
        return
    
    # default diffname is 'hard'
    diffname:str = 'hard'
    
    # output: filename-new-chart.json
    input_file:str = sys.argv[1]
    filename:str = os.path.basename(input_file)
    new_filename:str = filename.replace('.json', '-new-chart.json')
    new_metaFileName:str = filename.replace('.json', '-new-metadata.json')

    # if old output is specified, we will use that instead, and just add to the diff for it
    if len(sys.argv) == 4:
        new_filename:list = sys.argv[3]
        with open(new_filename, 'r') as f:
            newJsonData:list = json.load(f)
        new_metaFileName = new_filename.replace('.json', '-metadata.json')
        with open(new_metaFileName, 'r') as f:
            newMetadata:list = json.load(f)
    else:
        newJsonData:list = {
            "version": "2.0.0",
            "scrollSpeed": {"default": 1.0},
            "events": [],
            "notes": {
                diffname: []
            },
            "generatedBy": "FNF Chart Converter v1.0.0 - GuglioIsStupid"
        }
        newMetadata:list = {
            "timeFormat": "ms",
            "artist": "Unknown",
            "playData": {
                "album": "Unknown",
                "previewStart": 0,
                "previewEnd": 0,
                "stage": "Unknown",
                "characters": {
                    "player": "bf",
                    "opponent": "dad", 
                    "girlfriend": "gf"
                },
                "songVariations": [],
                "difficulties": [diffname],
                "noteStyle": "funkin"
            },
            "songName": "<CHANGE>",
            "timeChanges": [],
            "generatedBy": "FNF Chart Converter v1.0.0 - GuglioIsStupid",
            "looped": False,
            "version": "1.0.0"
        }

    diffsList = ["easy", "normal", "hard"]
    
    while diffname not in diffsList:
        diffname = input("Enter the difficulty of the chart (easy, normal, hard): ").lower()
        

    print(f"Converting {filename} to {new_filename}")

    with open(input_file, 'r') as f:
        song:list = json.load(f)["song"]

    newMetadata["songName"] = song["song"] if "song" in song else "<CHANGE>"

    curBpm:float = song["bpm"] if "bpm" in song else 120
    totalSteps:int = 0
    totalPos:float = 0

    newJsonData["scrollSpeed"]["default"] = song["speed"] if "speed" in song else 1.0
    newMetadata["timeChanges"].append({
        "t": 0,
        "d": 4,
        "n": 4,
        "bt": [4, 4, 4, 4],
        "bpm": curBpm
    })

    for section in song["notes"]:
        mustHit:bool = section["mustHitSection"]
        curBpm = section["bpm"] if "bpm" in section else curBpm

        for noteData in section["sectionNotes"]:
            # time, lane, holdtime
            # in new format, 0-3 is player 1, 4-7 is player 2
            # in old format, mustHit and 0-3 is player 1, 4-7 is player 2
            # !mustHit and 0-3 is player 2, 4-7 is player 1
            time:float = noteData[0]
            lane:int = noteData[1]
            holdTime:float = noteData[2] if len(noteData) > 3 else 0

            if mustHit:
                if lane < 4:
                    lane += 4
                else:
                    lane -= 4
            else:
                if lane < 4:
                    lane += 4
                else:
                    lane -= 4
           
            newNoteDic:list = {
                "t": time,
                "d": lane,
                "l": holdTime
            }

            newJsonData["notes"][diffname].append(newNoteDic)

        # from https://github.com/FunkinCrew/Funkin/blob/master/source/Conductor.hx#L35 lmfao
        deltaSteps:int = section["lengthInSteps"] if "lengthInSteps" in section else 16
        totalSteps += deltaSteps
        totalPos += ((60 / curBpm) * 1000 / 4) * deltaSteps

        focusCameraEvent:list = {
            "t": totalPos,
            "e": "FocusCamera",
            "v": {
                "char": mustHit and 0 or 1
            }
        }

        if section["changeBPM"]:
            timeChangeEvent:list = {
                "t": totalPos,
                "d": 4,
                "n": 4,
                "bt": [4, 4, 4, 4],
                "bpm": curBpm
            }

            newMetadata["timeChanges"].append(timeChangeEvent)

        newJsonData["events"].append(focusCameraEvent)

    with open(new_filename, 'w') as f:
        json.dump(newJsonData, f, indent=4)

    with open(new_metaFileName, 'w') as f:
        json.dump(newMetadata, f, indent=4)

if __name__ == "__main__":
    main()