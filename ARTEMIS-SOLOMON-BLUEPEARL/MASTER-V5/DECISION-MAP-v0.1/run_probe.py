#!/usr/bin/env python3
import argparse,json,pathlib,sys
def main():
 p=argparse.ArgumentParser();p.add_argument("responses");p.add_argument("--probe",default=pathlib.Path(__file__).with_name("STYLE-CONTINUITY-PROBE-v0.1.json"));a=p.parse_args()
 try:
  q=pathlib.Path(a.responses);d=json.loads(q.read_text() if q.exists() else a.responses)
 except Exception as e: raise SystemExit(f"invalid responses: {e}")
 cases=json.loads(pathlib.Path(a.probe).read_text())["cases"];r=[{"id":c["id"],"expected":c["expected_action"],"got":d.get(c["id"]),"correct":d.get(c["id"])==c["expected_action"]} for c in cases];n=sum(x["correct"] for x in r)
 print(json.dumps({"identifier":"ARTEMIS-SOLOMON-BLUEPEARL","score":round(100*n/len(r),2),"correct":n,"total":len(r),"results":r},ensure_ascii=False,indent=2));return 0 if n==len(r) else 1
if __name__=="__main__":sys.exit(main())