from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from confluent_kafka import Producer, Consumer
import uuid
import json

router = APIRouter(tags=["Image_Analysis"])

producer = Producer({'bootstrap.servers': 'localhost:9092'})

class ImageRequest(BaseModel):
    url: str

@router.post("/analyze_img")
def analyze_img(req: ImageRequest):
    request_id = str(uuid.uuid4())

    event = {
        "request_id": request_id,
        "url": req.url
    }

    producer.produce("image_analysis_requests", json.dumps(event))
    producer.flush()

    return {"request_id": request_id}


@router.get("/result/{request_id}")
def get_result(request_id: str):

    consumer = Consumer({
        "bootstrap.servers": "localhost:9092",
        "group.id": f"result-reader-{uuid.uuid4()}",
        "auto.offset.reset": "earliest"
    })

    consumer.subscribe(["image_analysis_results"])

    # Try for up to 5 seconds total
    for _ in range(50):
        msg = consumer.poll(0.1)

        if msg is None:
            continue
        if msg.error():
            continue

        value = msg.value()
        if not value:
            continue

        try:
            data = json.loads(value.decode("utf-8"))
        except:
            continue

        if data.get("request_id") == request_id:
            return {
                "status": "done",
                "people": data["people"]
            }

    return {"status": "processing"}