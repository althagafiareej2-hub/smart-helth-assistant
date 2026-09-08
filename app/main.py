from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.ai_analysis import analyze_symptoms
from app.database import SessionLocal, engine, Base
from app.models import PatientCase

Base.metadata.create_all(bind=engine)
app=FastAPI(title='مسار - المساعد الصحي الذكي',version='2.0')
app.mount('/static',StaticFiles(directory='static'),name='static')
templates=Jinja2Templates(directory='templates')
class PatientSymptoms(BaseModel): text:str
@app.get('/')
def home(request:Request): return templates.TemplateResponse(request=request,name='index.html',context={})
@app.get('/dashboard')
def dashboard(request:Request): return templates.TemplateResponse(request=request,name='dashboard.html',context={})
@app.post('/analyze')
def analyze(data:PatientSymptoms):
    result=analyze_symptoms(data.text); db=SessionLocal()
    try:
        case=PatientCase(symptoms_text=data.text,detected_symptoms=', '.join(result['detected_symptoms']),duration=result['duration'],severity=result['severity'],priority=result['priority'],doctor_summary=result['doctor_summary'])
        db.add(case); db.commit(); db.refresh(case); return {'case_id':case.id,**result}
    finally: db.close()
@app.get('/patterns')
def patterns():
    db=SessionLocal()
    try: cases=db.query(PatientCase).all()
    finally: db.close()
    now=datetime.utcnow(); recent_start=now-timedelta(days=7); previous_start=now-timedelta(days=14)
    recent=[c for c in cases if c.created_at and c.created_at>=recent_start]
    previous=[c for c in cases if c.created_at and previous_start<=c.created_at<recent_start]
    def count(items):
        out={}
        for c in items:
            for s in (c.detected_symptoms or '').split(', '):
                if s: out[s]=out.get(s,0)+1
        return out
    rc,pc=count(recent),count(previous); alerts=[]
    for s,n in rc.items():
        old=pc.get(s,0)
        if n>=3 and n>old: alerts.append({'symptom':s,'recent_cases':n,'previous_cases':old,'increase':n-old,'message':f'لوحظ ارتفاع في حالات {s}'})
    return {'total_cases':len(cases),'recent_cases':len(recent),'previous_cases':len(previous),'recent_symptom_frequency':rc,'previous_symptom_frequency':pc,'alerts':alerts,'note':'هذه المؤشرات للمساندة ورصد الأنماط الصحية وليست تشخيصًا طبيًا.'}
