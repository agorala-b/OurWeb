#!/bin/bash
# Tên file: build_help.sh
# Mục đích: Hỗ trợ user chạy web test local bằng Jekyll
# Sử dụng: sh scripts/build_help.sh

echo "Building and serving AgIL Static Site locally..."
echo "If you haven't installed Jekyll, please run: gem install bundler"
echo "------------------------------------------------------------------"

# Thiết lập thư mục cài bundle ở local để khỏi bị lỗi Permission
bundle config set --local path 'vendor/bundle' 
bundle check || bundle install

# Serve site at localhost:4000
bundle exec jekyll serve --livereload
