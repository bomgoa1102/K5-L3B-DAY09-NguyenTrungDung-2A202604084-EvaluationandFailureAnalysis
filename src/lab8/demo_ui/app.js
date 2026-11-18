const names = {workflow:'A — Workflow', single:'B — Single agent', orchestrator:'C — Orchestrator', swarm:'D — Swarm'};
const statuses = {resolved:'Đã giải quyết', denied:'Từ chối', needs_info:'Cần thêm thông tin', escalated:'Chuyển xử lý', failed:'Không thành công'};
const $ = id => document.getElementById(id);
const money = n => `${new Intl.NumberFormat('vi-VN').format(n ?? 0)} ₫`;
async function setup() {
  try {
    const res = await fetch('/api/benchmark');
    if (!res.ok) throw new Error();
    const data = await res.json();
    data.claims.forEach(claim => { const option = document.createElement('option'); option.value = claim; option.textContent = claim; $('claim').append(option); });
    $('benchmark').replaceChildren();
    Object.entries(names).forEach(([key, name]) => {
      const row = document.createElement('tr'); const d = data.shapes[key];
      [name, `${(d.pass_rate * 100).toFixed(d.pass_rate === 1 ? 0 : 2)}%`, d.pass_5.toFixed(3), `${d.cost_per_success_vnd.toFixed(2)} VND`, d.mean_model_calls.toFixed(2)].forEach(value => { const cell = document.createElement('td'); cell.textContent = value; row.append(cell); });
      $('benchmark').append(row);
    });
  } catch (_) { $('benchmark').innerHTML = '<tr><td colspan="5">Không tải được benchmark. Kiểm tra terminal.</td></tr>'; $('run').disabled = true; }
}
$('run').addEventListener('click', async () => {
  const button = $('run'); button.disabled = true; button.firstChild.textContent = 'Đang chạy… '; $('error').hidden = true;
  try {
    const res = await fetch('/api/run', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({shape:$('shape').value, claim:$('claim').value, seed:Number($('seed').value)})});
    const result = await res.json(); if (!res.ok) throw new Error(result.error || 'Không thể chạy.');
    $('empty').hidden = true; $('output').hidden = false;
    $('status').textContent = statuses[result.status] || result.status;
    $('run-id').textContent = result.run_id;
    $('proposal').textContent = money(result.proposal_amount); $('refund').textContent = money(result.refund_amount);
    $('model').textContent = result.model_calls; $('tools').textContent = result.tool_calls;
    $('reason').textContent = result.error_reason ? `Lý do: ${result.error_reason}` : '';
    $('events').replaceChildren(); result.events.forEach(event => {const item = document.createElement('span'); item.textContent = event; $('events').append(item);});
  } catch (err) { $('error').textContent = err.message || 'Có lỗi xảy ra.'; $('error').hidden = false; }
  finally {button.disabled = false; button.firstChild.textContent = 'Chạy tình huống ';}
});
setup();
