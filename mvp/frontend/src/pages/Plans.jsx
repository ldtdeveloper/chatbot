import React,{useState} from "react";
import { useQuery} from "@tanstack/react-query";
import { planService} from "../services/services";
import '../styles/Plans.css';
import ViewPlan from '../components/ViewPlan'
import PlanForm from "../components/PlanForm";
import { showError,showSuccess } from "../utils/toast";

export default function Plans() {
      const [showPlanDetail, setPlanDetail] = useState(false)
      const [selectedPlan, setSelectedPlan] = useState()
      const [showPlanForm, setPlanForm]  = useState(false)
      const { data: plans, isLoading ,refetch} = useQuery({
        queryKey: ['plans'],
        queryFn: planService.listPlan,
      })
      const handleViewPlan = (plan) => {
            console.log(`View plan clicked ${plan}`)
            setSelectedPlan(plan);
            setPlanDetail(true);
            console.log(`Selected plan ${selectedPlan}`)
        };

      const handleEditPlan = (plan) => {
            console.log(`Handle Edit button ..........${plan}`)
            setSelectedPlan(plan);
            setPlanForm(true);
      }

       const handleSubmit = async (submitData,initialData) => {
        setPlanForm(false);
        setSelectedPlan(null)
        let response = null
        try{
            if(initialData==null){
                response = await planService.createPlans(submitData)
                if(response?.id){
                    refetch()
                    showSuccess("Plan created successfully")
                    return
                }
                showError("Plan not created")
            }
            else{
                response = await planService.updatePlan(submitData.id,submitData)
                if(response?.id){
                    refetch()
                    showSuccess("Plan updated successfully")
                    return 
                }
                showError("Plan not updated")
            }
        }
        catch(err) {
            console.log(err)
            showError(err.message)
        }
      }

      const handleBack = () =>{
        setSelectedPlan(false);
        setPlanForm(false);
      }

      const handleIsActive= async (id,isActive) =>{
        try{
            const response = await planService.updatePlan(id,{"is_active": isActive})
            if(response?.id){
                refetch()
                if(isActive){
                    showSuccess("Plan activated")
                }
                else{
                    showSuccess("Plan deactivated")
                }
                return
            }
        }
        catch(err){
            showError(err.message)
        }
      }
      
      const handleDelete = async (id) => {
        try{
            const response = await planService.deletePlan(id)
            if(response.message!=""){
                refetch()
                showSuccess("Plan deleted successfully")
                return
            }
        }
        catch(err){
            showError(err.message)
        }
      }

      if (isLoading) return <div>Loading...</div>
    
      const planList = Array.isArray(plans) ? plans : [];
    return (
        <div className="plans">

            <div className="page-header">
            <h1>Plan Management</h1>
            <button onClick={() => setPlanForm(true)}>
            +  Add new plan
           </button>
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
                    className="view-btn" onClick={() => handleViewPlan(plan)}>
                    View
                    </button>

                    <button className="view-btn" onClick={() => handleEditPlan(plan)}>
                    Edit Plan
                    </button>

                    <button onClick={() => handleIsActive(plan.id,!plan.is_active)}>
                    {plan.is_active ? "Deactivate" : "Activate"}
                    </button>
                    <button className= "delete-btn" onClick={()=> handleDelete(plan.id)}>
                        Delete
                    </button>
                </div>
                </div>
            ))}
            {planList.length === 0 && <p>No plans found.</p>}
            </div>
            {showPlanDetail && selectedPlan && (
                <div className="modal-overlay" onClick={() => setPlanDetail(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                    <ViewPlan plan={selectedPlan} onBack={() => setPlanDetail(false) } />
                    </div>
                </div>
                )}
            {showPlanForm  && <PlanForm initialData = {selectedPlan? selectedPlan : null} onSubmit={handleSubmit} onBack={handleBack}/>}
        </div>
        )
}
