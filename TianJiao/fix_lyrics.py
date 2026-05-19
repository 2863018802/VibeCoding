import re

with open('d:/VibeCoding/TianJiao/520-website/index.html', encoding='utf-8') as f:
    content = f.read()

# Replace lyrics
old = '<span class="highlight">从你的故事里，</span>'
new = '甜蜜中<span class="highlight">不再畏高</span>'

# More surgical: line by line
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if '<span class="highlight">从你的故事里，</span>' in line:
        # Replace this block - skip the next few lines until the 5th lyric item
        # Find the range of the o3ic-item divs (5 of them)
        # Skip lines until we find the closing of 5th item
        # Strategy: replace from this line until the line containing "何必夸张成爱"
        j = i
        while j < len(lines) and '何必夸张成爱' not in lines[j]:
            j += 1
        # include the closing line
        j += 1

        replacements = [
            '    甜蜜中<span class="highlight">不再畏高</span>',
            '    天荒地老<span class="purple">流连在摩天轮</span>',
            '    <span class="highlight">惊栗之处</span>',
            '    仍能与<span class="purple">你互拥</span>',
            '    若问世界谁无双 — <span class="highlight">会令昨天明天也闪亮</span>',
        ]

        # Find which o3ic-item we're at based on position in the file
        # Just replace the content between the two markers
        print(f"Found lyrics at lines {i+1}-{j+1}")
        break
    new_lines.append(line)
    i += 1

# Better approach: find the section between o3ics-title and </section> in s2
# Let's just do a simple regex replacement

pattern = r'(<div class="o3ics-title">— 陈奕迅 · 歌词墙 —</div>)\s*<div class="o3ic-item" data-intersect>\s*<span class="highlight">从你的故事里，</span>\s*</div>\s*<div class="o3ic-item" data-intersect>\s*我终于读懂了为什么<span class="purple">爱一个人会心碎。</span>\s*</div>\s*<div class="o3ic-item" data-intersect>\s*<span class="highlight">我知，</span>\s*</div>\s*<div class="o3ic-item" data-intersect>\s*日后，路上<span class="purple">或没有更美的邂逅。</span>\s*</div>\s*<div class="o3ic-item" data-intersect>\s*若只是喜欢，<span class="highlight">何必夸张成爱。</span>\s*</div>'

replacement = r'''\1

  <div class="o3ic-item" data-intersect>
    甜蜜中<span class="highlight">不再畏高</span>
  </div>
  <div class="o3ic-item" data-intersect>
    天荒地老<span class="purple">流连在摩天轮</span>
  </div>
  <div class="o3ic-item" data-intersect>
    <span class="highlight">惊栗之处</span>
  </div>
  <div class="o3ic-item" data-intersect>
    仍能与<span class="purple">你互拥</span>
  </div>
  <div class="o3ic-item" data-intersect>
    若问世界谁无双 — <span class="highlight">会令昨天明天也闪亮</span>
  </div>'''

result, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
if count > 0:
    print(f"Replaced {count} occurrence(s)")
    with open('d:/VibeCoding/TianJiao/520-website/index.html', 'w', encoding='utf-8') as f:
        f.write(result)
    print("File written successfully")
else:
    print("Pattern not found - showing raw bytes")
    idx = content.find('从你的故事里')
    if idx >= 0:
        print(repr(content[idx-100:idx+200]))
