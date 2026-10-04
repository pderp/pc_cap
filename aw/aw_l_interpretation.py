"""Descriptive interpretation and historical cost-gate disclosure for AW-L6."""

from __future__ import annotations

from aw import reader_results as rr


def comparisons(cells):
    complete = {
        (c['dataset'], c['seed'], c['planned_read'], c['planned_write']): c
        for c in cells if c['status'] == 'complete'
    }
    rows = []
    for ds in rr.DATASETS:
        for seed in range(3):
            for read in ('all', 'upper'):
                a = complete.get((ds, seed, read, 'all'))
                b = complete.get((ds, seed, read, 'last'))
                if a is None or b is None:
                    continue
                diff = rr.paired(b, a)
                base_loss = a['harm']['capoff']['mean_delta_nll']
                rows.append(dict(
                    dataset=ds, seed=seed, read=read,
                    difference_last_minus_all=diff,
                    mean_loss_ratio=(b['harm']['capoff']['mean_delta_nll'] / base_loss
                                     if base_loss > 0 else None),
                ))
    return rows


def cost_gate(root, sources):
    """Disclose the completed owner's shell error; never repair/re-execute it."""
    projection = root / 'logs/additional_work/AW-L/portfolio-cost-20261003'
    chain = root / 'logs/additional_work/AW-L/awl5_chain_20261003.sh'
    if not projection.exists() or not chain.exists():
        return None
    data = rr.read(projection, sources)
    hours = rr.finite(data['projected_process_hours'])
    if hours < 0:
        raise ValueError('negative AW-L projection')
    sources[str(chain.resolve())] = rr.sha(chain)
    return dict(
        projection=str(projection), projected_process_hours=hours,
        original_shell=str(chain), shell_gate_hours=40,
        declared_ceiling_hours=data['upper_ceiling_hours'],
        projection_below_shell_gate=hours <= 40,
        gate_enforced=False,
        reason='The output is an extensionless JSON file. The shell searched for '
               'a directory of JSON files or a .json suffix, found neither, and '
               'defaulted to 0.0. This did not validate the budget.',
        followup='Before any future reuse, read the exact output file and explicit '
                 'projected_process_hours field; reject missing, invalid or '
                 'nonfinite input and a failed comparison. Do not use the maximum '
                 'of all hour-valued fields (which includes the 48-hour ceiling).',
        retrospective_only=True,
    )


def narrative(report):
    rows = report['write_comparisons']
    if len(rows) != 12:
        return 'The write comparison remains incomplete; no full factorial reading is assigned.\n\n'
    ratios = [x['mean_loss_ratio'] for x in rows if x['mean_loss_ratio'] is not None]
    delta = [x['difference_last_minus_all'] for x in rows]
    text = '## Reading of the completed factorial\n\n'
    if all(x['fired'] == 0 for x in delta):
        text += 'The last-only write mask leaves the ordinary-text firing count unchanged in all twelve paired write comparisons. '
    if all(x['mean_delta_nll'] > 0 for x in delta):
        text += ('Mean signed ordinary-text loss increase is greater with last-only writes in every pair; '
                 f'the per-pair ratio is {min(ratios):.2f}–{max(ratios):.2f}×. ')
    text += (f'The largest absolute paraphrase-retention change from the write restriction is '
             f'{100 * max(abs(x["RET-GS"]) for x in delta):.2f} percentage points. '
             'This tests the deployment/acquisition interface of readers trained with the full-write objective; '
             'it does not test separately retrained last-only writers.\n\n')
    text += rr.table(
        ['Dataset', 'Seed', 'Read', 'Last−all RET-GS (pp)', 'Last−all mean ΔNLL', 'Mean-loss ratio'],
        [[x['dataset'], x['seed'], x['read'],
          100 * x['difference_last_minus_all']['RET-GS'],
          x['difference_last_minus_all']['mean_delta_nll'], x['mean_loss_ratio']] for x in rows],
    )
    text += ('Read-tap effects and interactions are shown by seed below. Do not infer that lower layers '
             'are noise from a parameter reduction or unchanged firing under a write-only intervention. '
             'Intervals described as seed ranges are descriptive minimum–maximum ranges, not confidence intervals.\n\n')
    return text


def cost_note(report):
    gate = report.get('historical_cost_gate')
    if gate is None:
        return ''
    return (
        '\n\n### Historical budget-check defect\n\n'
        f'The saved profile projection was **{gate["projected_process_hours"]:.2f} process-hours**, '
        'below the shell\'s 40-hour gate and the declared 48-hour wall ceiling. It projected the full '
        'six-reader/24-cell design, including shared controls; it is not a forecast of incremental work alone. '
        'The shell gate did **not** enforce its check: it searched the wrong path and defaulted to 0.0. '
        'Actual new AW-L parent receipts sum to '
        f'**{report["incremental_aw_l_process_seconds"] / 3600:.3f} process-hours**; '
        'the owner reports about 9.7 wall-hours for the serial chain. Shared controls contribute to the '
        'attributed total above but are not new GPU work. Being under budget retrospectively does not '
        'mean the admission check worked. The original chain and projection are preserved; future reuse '
        'must read the exact file/field and reject missing or invalid input. No experiment was rerun.\n\n'
    )
