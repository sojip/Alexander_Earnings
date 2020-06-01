#Instructions to run the app
FROM python:3.7.4
WORKDIR /app/
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ENV GECKODRIVER_PATH "/usr/bin/geckodriver"
ENV FIREFOX_BIN "/usr/bin/firefox"
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["./application.py", "--host=0.0.0.0"]
