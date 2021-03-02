FROM python:3.7.4
WORKDIR /app
COPY ./ ./
RUN mkdir /app/data
RUN pip install -r requirements.txt
RUN apt update && apt install caffe-cpu --yes
RUN find /usr/lib/python3/dist-packages/caffe  -name "io.py" -exec sed -i "s/as_grey/as_gray/g" {} \;
ENV PYTHONPATH=/usr/lib/python3/dist-packages:
EXPOSE 8000
CMD ["uvicorn", "main:app","--reload", "--host","0.0.0.0"]