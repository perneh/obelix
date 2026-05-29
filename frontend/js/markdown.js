/**
 * Minimal markdown renderer for category help pages.
 * Supports headings, paragraphs, lists, tables, code blocks, and inline formatting.
 */

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderInline(text) {
  let html = escapeHtml(text);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return html;
}

function isTableRow(line) {
  return line.trim().startsWith("|") && line.trim().endsWith("|");
}

function parseTableRow(line) {
  return line
    .trim()
    .slice(1, -1)
    .split("|")
    .map((cell) => cell.trim());
}

function isTableSeparator(line) {
  return /^\|[\s\-:|]+\|$/.test(line.trim());
}

export function renderMarkdown(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const parts = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("```")) {
      const codeLines = [];
      i += 1;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(escapeHtml(lines[i]));
        i += 1;
      }
      parts.push(`<pre><code>${codeLines.join("\n")}</code></pre>`);
      i += 1;
      continue;
    }

    if (isTableRow(line) && i + 1 < lines.length && isTableSeparator(lines[i + 1])) {
      const headerCells = parseTableRow(line);
      i += 2;
      const bodyRows = [];
      while (i < lines.length && isTableRow(lines[i])) {
        bodyRows.push(parseTableRow(lines[i]));
        i += 1;
      }
      const thead = `<thead><tr>${headerCells.map((c) => `<th>${renderInline(c)}</th>`).join("")}</tr></thead>`;
      const tbody = bodyRows
        .map(
          (row) =>
            `<tr>${row.map((c) => `<td>${renderInline(c)}</td>`).join("")}</tr>`
        )
        .join("");
      parts.push(`<table>${thead}<tbody>${tbody}</tbody></table>`);
      continue;
    }

    if (/^#{1,3} /.test(line)) {
      const level = line.match(/^#+/)[0].length;
      const text = line.replace(/^#+\s*/, "");
      parts.push(`<h${level}>${renderInline(text)}</h${level}>`);
      i += 1;
      continue;
    }

    if (/^[-*] /.test(line)) {
      const items = [];
      while (i < lines.length && /^[-*] /.test(lines[i])) {
        items.push(`<li>${renderInline(lines[i].replace(/^[-*] /, ""))}</li>`);
        i += 1;
      }
      parts.push(`<ul>${items.join("")}</ul>`);
      continue;
    }

    if (/^\d+\. /.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(`<li>${renderInline(lines[i].replace(/^\d+\. /, ""))}</li>`);
        i += 1;
      }
      parts.push(`<ol>${items.join("")}</ol>`);
      continue;
    }

    if (line.trim() === "") {
      i += 1;
      continue;
    }

    const paraLines = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !/^#/.test(lines[i]) &&
      !/^[-*] /.test(lines[i]) &&
      !/^\d+\. /.test(lines[i]) &&
      !lines[i].startsWith("```") &&
      !isTableRow(lines[i])
    ) {
      paraLines.push(lines[i]);
      i += 1;
    }
    parts.push(`<p>${renderInline(paraLines.join(" "))}</p>`);
  }

  return parts.join("\n");
}
