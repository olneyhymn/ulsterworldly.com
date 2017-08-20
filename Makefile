SASSDIR='themes/bootstrap/static/assets/sass'
COMPILEDCSSDIR='themes/bootstrap/static/assets/_css'
S3_BUCKET='ulsterworldly.com'

all: build deploy

build: scss
	hugo --enableGitInfo

scss:
	cd themes/westminsterhist && npm run build

preview: scss
	# Launch local server to preview pages (with auto refresh)
	hugo server --watch --port 1313 --buildDrafts --buildFuture --quiet --log --ignoreCache

clean:
	# Delete local build
	rm -rf public
	cd themes/westminsterhist && npm run clean

deploy: build
	# Deploy site to heroku
	s3cmd sync --acl-public --delete-removed --guess-mime-type --no-mime-magic public/ s3://$(S3_BUCKET)
	python3 build_scripts/invalidate_cloudfront.py

push:
	# Push to github
	git push

pdfs:
	# Generate PDFs from HTML pages (esp opc.org pages)
	. make_pdfs.sh

archive_pdfs:
	# Archive pdf files from other sites... just in case.
	. archive_pdfs.sh
