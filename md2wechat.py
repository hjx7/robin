"""把 Hexo markdown 文章转成微信公众号 HTML（内联样式，可直接粘贴）"""
import re, os, sys

def md_to_wechat_html(md_text):
    # 去掉 front matter
    md_text = re.sub(r'^---\n.*?\n---\n', '', md_text, flags=re.DOTALL)

    lines = md_text.split('\n')
    html_parts = []
    in_list = False
    in_numbered = False
    list_items = []
    list_type = None

    def flush_list():
        nonlocal list_items, in_list, in_numbered, list_type
        if not list_items:
            return
        bg = '#fff2e8' if list_type == 'danger' else '#f7f7f7'
        border = 'border-left:4px solid #d4380d;border-radius:0 6px 6px 0;' if list_type == 'danger' else ''
        style = f'background:{bg};{border}border-radius:6px;padding:14px 18px;margin:0 0 18px;'
        items_html = ''.join(f'<p style="margin:0 0 6px;">{item}</p>' for item in list_items)
        if list_items and list_items[-1].endswith('</p>'):
            # last item already has margin 0 from the join, fix it
            pass
        # Fix last item margin
        items_html = items_html.replace('margin:0 0 6px;">{item}</p>'.format(item=list_items[-1]), 'margin:0;">{item}</p>'.format(item=list_items[-1]))
        html_parts.append(f'<section style="{style}">{items_html}</section>')
        list_items = []
        in_list = False
        in_numbered = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # H1
        if stripped.startswith('# ') and not stripped.startswith('## '):
            title = stripped[2:].strip()
            html_parts.append(f'<section style="text-align:center;margin-bottom:30px;"><h1 style="font-size:22px;font-weight:bold;color:#1a1a1a;line-height:1.5;margin:0;">{title}</h1></section>')
            i += 1
            continue

        # H2
        if stripped.startswith('## '):
            if in_list:
                flush_list()
            title = stripped[3:].strip()
            html_parts.append(
                '<section style="margin:32px 0 20px;">'
                '<section style="display:flex;align-items:center;margin-bottom:16px;">'
                '<section style="width:5px;height:20px;background:#d4380d;border-radius:3px;margin-right:10px;"></section>'
                f'<h2 style="font-size:18px;font-weight:bold;color:#1a1a1a;margin:0;">{title}</h2>'
                '</section></section>'
            )
            i += 1
            continue

        # H3
        if stripped.startswith('### '):
            if in_list:
                flush_list()
            title = stripped[4:].strip()
            html_parts.append(f'<h3 style="font-size:16px;font-weight:bold;color:#1a1a1a;margin:24px 0 14px;">{title}</h3>')
            i += 1
            continue

        # Image
        if stripped.startswith('!['):
            if in_list:
                flush_list()
            alt = re.match(r'!\[(.*?)\]\((.*?)\)', stripped)
            if alt:
                src = alt.group(2)
                alt_text = alt.group(1)
                # Convert relative path to file:/// absolute path
                if src.startswith('/'):
                    src = 'file:///g:/hjx7/robin/source' + src
                html_parts.append(f'<section style="text-align:center;margin-bottom:20px;"><img src="{src}" style="max-width:100%;border-radius:4px;" alt="{alt_text}" /></section>')
            i += 1
            continue

        # Table
        if stripped.startswith('|'):
            if in_list:
                flush_list()
            # Collect all table lines
            table_lines = [stripped]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('|'):
                table_lines.append(lines[j].strip())
                j += 1
            # Parse table
            rows = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.split('|')[1:-1]]
                rows.append(cells)
            # Skip separator row (---)
            rows = [r for r in rows if not all(c.replace('-','').replace(':','') == '' for c in r)]
            if rows:
                table_html = '<section style="margin:0 0 18px;">'
                table_html += '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
                for ri, row in enumerate(rows):
                    table_html += '<tr>'
                    for cell in row:
                        if ri == 0:
                            table_html += f'<th style="border:1px solid #e0e0e0;padding:8px 10px;background:#f7f7f7;font-weight:bold;text-align:left;">{cell}</th>'
                        else:
                            table_html += f'<td style="border:1px solid #e0e0e0;padding:8px 10px;">{cell}</td>'
                    table_html += '</tr>'
                table_html += '</table></section>'
                html_parts.append(table_html)
            # Skip the table lines we already processed
            i = j
            continue

        # Bullet list
        if re.match(r'^[-*]\s', stripped):
            in_list = True
            item = re.sub(r'^[-*]\s+', '', stripped)
            item = format_inline(item)
            list_items.append(f'• {item}')
            i += 1
            continue

        # Numbered list
        if re.match(r'^\d+\.\s', stripped):
            in_list = True
            num = re.match(r'^(\d+)\.\s', stripped).group(1)
            item = re.sub(r'^\d+\.\s+', '', stripped)
            item = format_inline(item)
            list_items.append(f'{num}. {item}')
            i += 1
            continue

        # Empty line
        if not stripped:
            if in_list:
                flush_list()
            i += 1
            continue

        # Regular paragraph
        if in_list:
            flush_list()

        para = format_inline(stripped)
        # Check if it's a "highlight" paragraph (all bold)
        if stripped.startswith('**') and stripped.endswith('**') and stripped.count('**') == 2:
            inner = stripped[2:-2]
            html_parts.append(f'<section style="background:#fff2e8;border-radius:6px;padding:18px 20px;margin:0 0 18px;text-align:center;"><p style="margin:0;font-size:16px;font-weight:bold;color:#d4380d;line-height:1.7;">{format_inline(inner)}</p></section>')
        else:
            html_parts.append(f'<p style="margin:0 0 18px;">{para}</p>')
        i += 1

    if in_list:
        flush_list()

    # Wrap
    wrapper = (
        '<section style="max-width:578px;margin:0 auto;padding:20px 16px;'
        "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
        'font-size:15px;line-height:1.8;color:#3f3f3f;letter-spacing:0.5px;word-break:break-word;">\n'
        + '\n'.join(html_parts)
        + '\n</section>'
    )
    return wrapper


def format_inline(text):
    # Bold: **text** → <strong style="color:#d4380d;">text</strong>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#d4380d;">\1</strong>', text)
    # Italic: *text* → <em>text</em>
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    # Inline code: `text` → <code>text</code>
    text = re.sub(r'`(.+?)`', r'<code style="background:#f0f0f0;padding:2px 5px;border-radius:3px;font-size:13px;">\1</code>', text)
    return text


def main():
    posts_dir = r'g:\hjx7\robin\source\_posts'
    output_dir = r'g:\hjx7\robin\knowledge-repository\宠物知识库\04-成稿'

    pet_articles = [
        '换过四种猫碗-我才敢说哪一种真的值得买.md',
        '新猫到家第一个月该怎么做.md',
        '猫下巴那堆小黑点-八成是塑料碗坑的.md',
        '猫只吃猫粮可以吗.md',
        '猫水盆的选择.md',
        '猫耳朵一股酸臭味-扒开全是黑泥-这玩意儿叫马拉色菌.md',
    ]

    for article in pet_articles:
        md_path = os.path.join(posts_dir, article)
        if not os.path.exists(md_path):
            print(f'跳过（文件不存在）: {article}')
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        html = md_to_wechat_html(md_text)

        # Output filename: replace .md with -公众号版.html
        out_name = article.replace('.md', '-公众号版.html')
        out_path = os.path.join(output_dir, out_name)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f'已转换: {out_name}')

    print(f'\n完成，共转换 {len(pet_articles)} 篇文章')


if __name__ == '__main__':
    main()
