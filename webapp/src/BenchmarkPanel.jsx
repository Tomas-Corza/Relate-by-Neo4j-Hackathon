import React,{useState} from 'react';
import responses from './benchmark-data/raw_responses.json';
import results from './benchmark-data/results.json';
import manifest from './benchmark-data/manifest.json';
import protocol from '../../benchmark_protocol.json';
import './benchmark.css';

const arms=['A','B','N'];
const names={A:'Campaign metrics only',B:'Context-rich flat data',N:'OpenClaw Nexus'};
const labels={factual_accuracy:'Factual accuracy',relationship_identification:'Relationship identification',evidence_completeness:'Evidence completeness',recommendation_quality:'Recommendation quality',unsupported_claims_avoidance:'Unsupported claims avoidance'};
const stats=Object.fromEntries(arms.map(a=>{
 const rows=responses.filter(r=>r.arm===a&&r.status==='ok');
 const total=k=>rows.reduce((s,r)=>s+r[k],0);
 return [a,{n:rows.length,input:total('input_tokens'),output:total('output_tokens'),seconds:total('elapsed_seconds')/rows.length,cap:rows.filter(r=>r.output_tokens>=manifest.max_completion_tokens).length}];
}));
const pct=v=>v.toFixed(2)+'%';
const num=v=>v.toLocaleString('en-US');
const reduction=(k)=>100*(1-stats.N[k]/stats.B[k]);
const repo='https://github.com/Tomas-Corza/Relate-by-Neo4j-Hackathon/blob/main/';
function Bars({title,metric,format,description}){
 const max=Math.max(...arms.map(metric));
 return <div className="bench-chart"><h3>{title}</h3>{arms.map(a=><div className="bench-bar-row" key={a}><div className="bench-bar-label"><span>{names[a]}</span><b>{format(metric(a))}</b></div><div className="bench-track"><div className={'bench-fill bench-'+a} style={{width:100*metric(a)/max+'%'}}/></div></div>)}<p>{description}</p></div>
}
export function BenchmarkPanel(){
 const [question,setQuestion]=useState('Q1');
 return <section className="surface workspace-section benchmark-panel">
 <div className="bench-heading"><div><small>RESEARCH &amp; VALIDATION · NOVEMBER 25, 2026</small><h2>Connected intelligence benchmark</h2></div><span className="bench-status">18 / 18 responses</span></div>
 <p>Completed experiment · AI-assisted scoring, partially blinded. Independent human validation pending. Six synthetic business questions, three context-delivery approaches, one model: {responses[0].resolved_model}.</p>
 <div className="analysis-kpis">
 {[['Fewer input tokens vs flat data',pct(reduction('input'))],['Lower mean API latency vs flat data',pct(reduction('seconds'))],['Nexus weighted quality',pct(results.N.weighted_score)],['Nexus evidence completeness',pct(results.N.criteria_pct.evidence_completeness)]].map(([n,v])=><div key={n}><small>{n}</small><strong>{v}</strong></div>)}
 </div>
 <p>Nexus matched the flat-data baseline's factual accuracy but scored {(results.B.weighted_score-results.N.weighted_score).toFixed(2)} percentage points lower overall. Its measured advantage was context efficiency, not universal answer superiority.</p>
 <div className="bench-charts"><Bars title="Weighted answer quality" metric={a=>results[a].weighted_score} format={pct} description="Higher is better · weighted rubric score out of 100."/><Bars title="Input token consumption" metric={a=>stats[a].input} format={num} description="Lower is better · total prompt tokens across six questions."/><Bars title="Mean API response duration" metric={a=>stats[a].seconds} format={v=>v.toFixed(2)+' s'} description="Lower is better · provider calls only, excluding context preparation."/></div>
 <h3>Quality and efficiency comparison</h3><div className="comparison-scroll"><table className="workspace-table"><thead><tr><th>Metric</th><th>Weight</th>{arms.map(a=><th key={a}>{names[a]}</th>)}</tr></thead><tbody>
 {Object.entries(labels).map(([k,label])=><tr key={k}><td>{label}</td><td>{protocol.weights[k]}%</td>{arms.map(a=><td key={a}>{pct(results[a].criteria_pct[k])}</td>)}</tr>)}
 <tr><th>Weighted score</th><td>100%</td>{arms.map(a=><th key={a}>{pct(results[a].weighted_score)}</th>)}</tr>
 {[['Input tokens',a=>num(stats[a].input)],['Output tokens',a=>num(stats[a].output)],['Total tokens',a=>num(stats[a].input+stats[a].output)],['Average input tokens per question',a=>num(Math.round(stats[a].input/stats[a].n))],['Mean API duration',a=>stats[a].seconds.toFixed(2)+' s'],['Responses at output cap',a=>stats[a].cap],['Successful requests',a=>stats[a].n+'/6']].map(([label,fn])=><tr key={label}><td>{label}</td><td>—</td>{arms.map(a=><td key={a}>{fn(a)}</td>)}</tr>)}
 </tbody></table></div>
 <h3>What we tested</h3><p>A receives campaign metrics only. B receives full flat records plus the same derived analytical tables and parameters as Nexus. Nexus receives executed, task-specific Relate tool evidence. All arms use identical questions, system instructions, model and 500-token response cap.</p>
 <details><summary>Inspect individual responses and evidence</summary><label>Benchmark question <select value={question} onChange={e=>setQuestion(e.target.value)}>{protocol.cases.map(c=><option key={c.id} value={c.id}>{c.id} · {c.question}</option>)}</select></label><p><b>Expected answer:</b> {protocol.cases.find(c=>c.id===question).expected}</p><div className="bench-responses">{arms.map(a=>{const r=responses.find(r=>r.arm===a&&r.question_id===question);return <article className="bench-response" key={a}><h4>{names[a]}</h4><small>{r.response_id} · {num(r.input_tokens)} input / {num(r.output_tokens)} output tokens · {r.elapsed_seconds.toFixed(2)} s{r.output_tokens>=manifest.max_completion_tokens?' · output cap reached':''}</small><div className="bench-response-text">{r.response}</div></article>})}</div></details>
 <h3>Interpretation and limitations</h3><p>One trial per arm and question, synthetic development-set data, no independent human validation or statistical significance test. Evidence format can reveal the arm. Reference calculations reuse existing analytics; algorithm correctness was not independently validated. The flat-data baseline has deliberately broad context; optimized flat retrieval was not tested. Three responses reached the output cap; financial attribution invariance and scenario qualification need improvement. Timing excludes database queries and context construction; token counts do not establish actual billed savings. An initial run failed all 18 calls on authentication and was excluded from scoring; the second run completed.</p>
 <div className="bench-links">{[['Methodology and reproduction','BENCHMARK.md'],['Raw responses','webapp/src/benchmark-data/raw_responses.json'],['Scoring rationale (CSV)','webapp/src/benchmark-data/scorecard.csv'],['Reference answers','webapp/src/benchmark-data/reference_answers.json'],['Scores','webapp/src/benchmark-data/results.json'],['Run manifest','webapp/src/benchmark-data/manifest.json']].map(([label,p])=><a key={p} href={repo+p} target="_blank" rel="noreferrer">{label} ↗</a>)}</div>
 </section>
}
