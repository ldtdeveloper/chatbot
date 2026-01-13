import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { planService, authService } from "../services/services";
import '../styles/Plans.css';

export default function Plans() {
      const navigate = useNavigate()

      const { data: plans, isLoading } = useQuery({
        queryKey: ['plans'],
        queryFn: planService.listPlan(),
      })
    
      if (isLoading) return <div>Loading...</div>
    
      const planList = plans?.length? plans: [];

    return (
        <div className="plans">
            <div className="page-header">
            <h1>Plan Management</h1>
            </div>
            <div className="plans-list">
            {planList.length!=0 && planList.map((plan) => (
                <div key={plan.id} className="plan-card">
                <div className="plan-info">
                    <h3>{plan.name}</h3>
                    <span className="plan-code">{plan.code}</span>

                    <p className="plan-description">
                    {plan.description}
                    </p>

                    <div className="plan-meta">
                    <span className="plan-price">
                        ₹{plan.price}
                    </span>

                    <span className="plan-credits">
                        {plan.credits} credits
                    </span>

                    <span
                        className={`status ${plan.is_active ? "active" : "inactive"}`}
                    >
                        {plan.is_active ? "Active" : "Inactive"}
                    </span>
                    </div>
                </div>

                <div className="plan-actions">
                    <button
                    className="view-btn"
                    onClick={() => navigate(`/plans/${plan.id}`)}
                    >
                    View
                    </button>

                    <button className="view-btn">
                    Edit Plan
                    </button>

                    <button>
                    {plan.is_active ? "Deactivate" : "Activate"}
                    </button>
                </div>
                </div>
            ))}
            {planList.length === 0 && <p>No plans found.</p>}
            </div>
        </div>
        )

}
