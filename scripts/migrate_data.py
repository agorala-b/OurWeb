import os
import glob
import yaml

# Tên file: migrate_data.py
# Mục đích: Chuyển đổi dữ liệu từ member/*.yml sang _people/*.md
# Test: Kiểm tra thư mục _people có file md và assets/images/people có hình ảnh

members_dir = 'member'
people_dir = '_people'
images_dir = 'assets/images/people'

os.makedirs(people_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

yaml_files = glob.glob(os.path.join(members_dir, '**', '*.yml'), recursive=True)

role_mapping = {
    'chair': 'Executive Board',
    'co-chair': 'Executive Board',
    'director': 'Executive Board',
    'member': 'Executive Board',  # some default
    'research assistant': 'Research Assistants',
    'intern': 'Interns',
    'alumni': 'Alumni'
}

order_mapping = {
    'Executive Board': 1,
    'Research Assistants': 2,
    'Interns': 3,
    'Alumni': 4
}


for yml_file in yaml_files:
    try:
        with open(yml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if not data: continue
        
        name = data.get('name', 'Unknown')
        slug = name.lower().replace(' ', '-').replace('đ', 'd')
        # handle special vietnamese chars roughly
        for c in "áàảãạăắằẳẵặâấầẩẫậ": slug = slug.replace(c, 'a')
        for c in "éèẻẽẹêếềểễệ": slug = slug.replace(c, 'e')
        for c in "íìỉĩị": slug = slug.replace(c, 'i')
        for c in "óòỏõọôốồổỗộơớờởỡợ": slug = slug.replace(c, 'o')
        for c in "úùủũụưứừửữự": slug = slug.replace(c, 'u')
        for c in "ýỳỷỹỵ": slug = slug.replace(c, 'y')
        
        md_file = os.path.join(people_dir, f"{slug}.md")
        
        job_title = data.get('title', 'Member')
        job_lower = job_title.lower()
        role_group = 'Executive Board' # as fallback
        
        for k, v in role_mapping.items():
            if k in job_lower:
                role_group = v
                break
        
        frontmatter = {
            'layout': 'person',
            'title': name,
            'job_title': job_title,
            'role_group': role_group,
            'order': order_mapping.get(role_group, 99),
            'department': data.get('department', ''),
            'email': data.get('email', ''),
            'linkedin': data.get('linkedin', ''),
            'github': data.get('github', ''),
            'scholar': data.get('scholar', '')
        }
        
        # Move image
        photo = data.get('photo', '')
        if photo:
            source_img = os.path.join(os.path.dirname(yml_file), photo)
            if os.path.exists(source_img):
                target_img = os.path.join(images_dir, photo)
                os.system(f'cp "{source_img}" "{target_img}"')
                frontmatter['photo'] = '/assets/images/people/' + photo
            else:
                frontmatter['photo'] = '/assets/images/logo.png' # default
        
        # additional lists
        frontmatter['educations'] = data.get('educations', [])
        frontmatter['awards'] = data.get('awards', [])
        frontmatter['services'] = data.get('services', {})
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('---\n')
            yaml.dump(frontmatter, f, allow_unicode=True, default_flow_style=False)
            f.write('---\n\n')
            f.write(data.get('about', ''))
            
        print(f"Migrated {name} to {md_file}")
            
    except Exception as e:
        print(f"Error processing {yml_file}: {e}")

print("Done migrating people.")
