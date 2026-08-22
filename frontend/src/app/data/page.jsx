"use client";
import Link from "next/link";
import { useDataset } from "../components/DatasetContext";
import DataInspector from "../DataInspector";
import DatasetSummary from "../DatasetSummary";
import { Card, Button } from "../components/ui";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { ArrowRight, Wrench } from "lucide-react";

export default function RawDataPage() {
  const { id } = useDataset();

  if (!id) {
    return (
      <main className="p-8 text-center">
        <Card title="No Dataset Selected">
          <p className="text-xs text-slate-500 mb-4">Please upload or select a dataset on the Overview page to explore raw rows.</p>
          <Link href="/"><Button size="sm">Go to Overview</Button></Link>
        </Card>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-6xl space-y-5 px-6 py-6 overflow-x-clip">
      <Breadcrumbs
        crumbs={[
          { href: "/", label: "Home" },
          { href: "/data", label: "Data Pipeline" },
          { label: "Raw Data Explorer" },
        ]}
      />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Raw Data Explorer</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Inspect canonical raw snapshot, column semantic dictionary, and field health before transformations
          </p>
        </div>
        <Link href="/cleaning">
          <Button size="sm" variant="primary">
            <Wrench size={13} /> Open Cleaning Studio <ArrowRight size={13} />
          </Button>
        </Link>
      </div>

      <DatasetSummary datasetId={id} />
      <DataInspector datasetId={id} defaultStage="raw" />
    </main>
  );
}
